#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:12:45 2020

@author: henry
"""

import numpy as np
import quaternion
from Input import Variables
from numpy.random import Generator, PCG64, SeedSequence


vec_z = np.array([0, 0, 1])
pi = np.pi

# %% Tumble Functions


def Normalise(vec):
    return vec/np.linalg.norm(vec)


def MakeRotationQuaternion(angle, vec):
    a = np.cos(angle/2)
    b = np.sin(angle/2)
    axis = vec*b
    axis = np.append(a, axis)
    quat = quaternion.from_float_array(axis)
    return quat


def Tumble(diff_angle, spin_angle, vec_int):
    diff_vec = Normalise(np.cross(vec_int, vec_z))
    diff_quat = MakeRotationQuaternion(diff_angle, diff_vec)
    vec_mid = quaternion.rotate_vectors(diff_quat, vec_int)
    spin_vec = Normalise(vec_int)
    spin_quat = MakeRotationQuaternion(spin_angle, spin_vec)
    vec_final = quaternion.rotate_vectors(spin_quat, vec_mid)
    return vec_final

# %% Bacterium Class Initialisation


class Bacterium:

    def __init__(self, fname):
        self.vars = Variables(fname)
        self.seed = SeedSequence()
        self.rand_gen = Generator(PCG64(self.seed))
        self.vector_initial = Normalise(self.rand_gen.uniform(-1,1,3))
        self.pos_initial = np.array([0, 0, 0])
        self.time = np.full(self.vars.sample_total, self.vars.base_time)
        self.time = np.append([0], self.time)
        self.time = np.cumsum(self.time)
        self.time = np.reshape(self.time, (self.time.size, 1))

# %% Extra Functions

    def ReSeed(self, entropy):
        self.seed = SeedSequence(entropy)
        self.rand_gen = Generator(PCG64(self.seed))

    def Linear(self):
        self.std_dev_linear = np.sqrt(2*self.vars.diffusion_constant_linear
                                      * self.vars.base_time)
        self.linear_diffusion = np.random.normal(
            0.0, self.std_dev_linear, (self.vars.sample_total, 3))

    def Rotational(self):
        self.std_dev_rotational\
            = np.sqrt(2*self.vars.diffusion_constant_rotational
                      * self.vars.base_time)
        self.rotational_sample = self.rand_gen.normal(
            0.0, self.std_dev_rotational, (2, self.vars.sample_total))
        self.diffusion_sample = np.sqrt(np.square(self.rotational_sample[0])
                                        + np.square(self.rotational_sample[1]))
        self.spin_sample = self.rand_gen.random(self.vars.sample_total)*2*pi
        self.vectors_cartesian_diffusion\
            = np.zeros((self.vars.sample_total, 3))
        self.vectors_cartesian_diffusion[0] = Tumble(self.diffusion_sample[0],
                                                     self.spin_sample[0],
                                                     self.vector_initial)
        for i in range(1, self.vars.sample_total):
            self.vectors_cartesian_diffusion[i]\
                = Tumble(self.diffusion_sample[i],
                         self.spin_sample[i],
                         self.vectors_cartesian_diffusion[i-1])

# %% Simulation Code Path

    def Complete(self):
        # Diffusion Sampling
        if self.vars.diffusive:
            self.std_dev_linear = np.sqrt(2*self.vars.diffusion_constant_linear
                                      * self.vars.base_time)
            self.linear_diffusion = self.rand_gen.normal(
                0.0, self.std_dev_linear, (self.vars.sample_total, 3))
            self.std_dev_rotational\
                = np.sqrt(2*self.vars.diffusion_constant_rotational
                          * self.vars.base_time)
            self.rotational_sample = self.rand_gen.normal(
                0.0, self.std_dev_rotational, (2, self.vars.sample_total))
            self.diffusion_sample = np.sqrt(np.square(self.rotational_sample[0])
                                            + np.square(self.rotational_sample[1]))
            self.spin_sample = self.rand_gen.uniform(
                0.0, 2*pi, self.vars.sample_total)
        else:
            self.linear_diffusion = np.zeros((self.vars.sample_total, 3))
            self.diffusion_sample = np.zeros(self.vars.sample_total)
            self.spin_sample = np.zeros(self.vars.sample_total)

        # Data Array Initialisation
        self.vectors_cartesian = np.zeros((self.vars.sample_total, 3))
        self.vectors_cartesian = np.vstack(
            (self.vector_initial, self.vectors_cartesian))
        self.displacement = np.zeros((self.vars.sample_total, 3))

        # Linear Diffusion
        self.displacement += self.linear_diffusion
        self.displacement = np.vstack((self.pos_initial, self.displacement))
        if self.vars.chemotactic:
            self.state = 'run_chemotactic'
            self.chemotactic_memory\
                = [0 for x in range(self.vars.chem_mem_size)]
        else:
            self.state = 'run'
        self.elapsed_time = 0
        self.run_log = []
        self.tumble_log = []  # Logs Run&Tumble Behaviour
        self.run_run_cosines = []

        if self.vars.run_behaviour is True:

            while self.elapsed_time < self.vars.sample_total:

                # %% Run Mode - Non Chemotactic

                if self.state == 'run':

                    if self.vars.run_variation is True:
                        current_run_length = int(np.ceil(
                            self.rand_gen.exponential(
                                self.vars.run_length_mean)))

                    else:
                        current_run_length = self.vars.run_length_mean

                    elapsed_run_length = 0

                    while elapsed_run_length < current_run_length:
                        if self.elapsed_time >= self.vars.sample_total:
                            break
                        i = self.elapsed_time
                        if self.vars.diffusive:
                            self.vectors_cartesian[i+1]\
                                = Tumble(self.diffusion_sample[i],
                                         self.spin_sample[i],
                                         self.vectors_cartesian[i])
                        else:
                            self.vectors_cartesian[i+1] = self.vectors_cartesian[i]

                        self.displacement[i+1]\
                            += self.vectors_cartesian[i+1]\
                            * self.vars.run_step

                        self.elapsed_time += 1
                        elapsed_run_length += 1

                    self.run_log.append(elapsed_run_length)

                    if self.vars.archaea_mode:
                        self.state = 'reverse'
                    else:
                        self.state = self.vars.tumble_type

                # %% Run Mode - Chemotactic

                elif self.state == 'run_chemotactic':

                    if self.vars.run_variation is True:
                        current_run_length = int(np.ceil(
                            self.rand_gen.exponential(
                                self.vars.run_length_mean)))

                    else:
                        current_run_length = self.vars.run_length_mean

                    elapsed_run_length = 0
                    chemotactic_factor = np.mean(self.chemotactic_memory)\
                        * self.vars.chem_factor
                    if chemotactic_factor < 0:
                        chemotactic_factor = 0
                    chemotactic_run_length = current_run_length\
                        * (chemotactic_factor + 1)

                    while elapsed_run_length < chemotactic_run_length:
                        if self.elapsed_time >= self.vars.sample_total:
                            break
                        i = self.elapsed_time
                        if self.vars.diffusive:
                            self.vectors_cartesian[i + 1] \
                                = Tumble(self.diffusion_sample[i],
                                         self.spin_sample[i],
                                         self.vectors_cartesian[i])
                        else:
                            self.vectors_cartesian[i + 1] = self.vectors_cartesian[i]

                        self.displacement[i+1]\
                            += self.vectors_cartesian[i+1]\
                            * self.vars.run_step

                        self.elapsed_time += 1
                        elapsed_run_length += 1

                        chemotactic_value = np.dot(
                            self.vectors_cartesian[i+1],
                            self.vars.chem_source)
                        self.chemotactic_memory.pop(0)
                        self.chemotactic_memory.append(chemotactic_value)
                        chemotactic_factor = np.mean(self.chemotactic_memory)\
                            * self.vars.chem_factor
                        if chemotactic_factor < 0:
                            chemotactic_factor = 0
                        chemotactic_run_length = current_run_length\
                            * (chemotactic_factor + 1)

                    self.run_log.append(elapsed_run_length)

                    if self.vars.archaea_mode:
                        self.state = 'reverse_chemotactic'
                    else:
                        self.state = self.vars.tumble_type

                # %% Reverse Mode - For Archaea

                elif self.state == 'reverse':

                    if self.vars.run_variation is True:
                        current_run_length = int(np.ceil(
                            self.rand_gen.exponential(
                                self.vars.run_length_mean)))

                    else:
                        current_run_length = self.vars.run_length_mean

                    elapsed_run_length = 0

                    while elapsed_run_length < current_run_length:
                        if self.elapsed_time >= self.vars.sample_total:
                            break
                        i = self.elapsed_time
                        if self.vars.diffusive:
                            self.vectors_cartesian[i + 1] \
                                = Tumble(self.diffusion_sample[i],
                                         self.spin_sample[i],
                                         self.vectors_cartesian[i])
                        else:
                            self.vectors_cartesian[i + 1] = self.vectors_cartesian[i]

                        self.displacement[i+1]\
                            += self.vectors_cartesian[i+1]\
                            * -self.vars.run_step

                        self.elapsed_time += 1
                        elapsed_run_length += 1

                    self.run_log.append(elapsed_run_length)

                    self.state = 'run'

                # %% Reverse Mode - For Chemotactic archaea

                elif self.state == 'reverse_chemotactic':

                    if self.vars.run_variation is True:
                        current_run_length = int(np.ceil(
                            self.rand_gen.exponential(
                                self.vars.run_length_mean)))

                    else:
                        current_run_length = self.vars.run_length_mean

                    elapsed_run_length = 0
                    chemotactic_factor = np.mean(self.chemotactic_memory)\
                        * self.vars.chem_factor
                    if chemotactic_factor < 0:
                        chemotactic_factor = 0
                    chemotactic_run_length = current_run_length\
                        * (chemotactic_factor + 1)

                    while elapsed_run_length < chemotactic_run_length:
                        if self.elapsed_time >= self.vars.sample_total:
                            break
                        i = self.elapsed_time
                        if self.vars.diffusive:
                            self.vectors_cartesian[i + 1] \
                                = Tumble(self.diffusion_sample[i],
                                         self.spin_sample[i],
                                         self.vectors_cartesian[i])
                        else:
                            self.vectors_cartesian[i + 1] = self.vectors_cartesian[i]

                        self.displacement[i+1]\
                            += self.vectors_cartesian[i+1]\
                            * -self.vars.run_step

                        self.elapsed_time += 1
                        elapsed_run_length += 1

                        chemotactic_value = np.dot(-self.vectors_cartesian[i+1],
                                                   self.vars.chem_source)
                        self.chemotactic_memory.pop(0)
                        self.chemotactic_memory.append(chemotactic_value)
                        chemotactic_factor = np.mean(self.chemotactic_memory)\
                            * self.vars.chem_factor
                        if chemotactic_factor < 0:
                            chemotactic_factor = 0
                        chemotactic_run_length = current_run_length\
                            * (chemotactic_factor + 1)

                    self.run_log.append(elapsed_run_length)

                    self.state = 'run_chemotactic'

                # %% Erratic Tumble Mode

                elif self.state == 'erratic':

                    if self.vars.tumble_duration_mean == 0:
                        current_tumble_length = 0

                    elif self.vars.tumble_duration_variation is True:
                        current_tumble_length\
                            = int(np.ceil(self.rand_gen.exponential(
                                self.vars.tumble_length_mean)))

                    else:
                        current_tumble_length\
                            = self.vars.tumble_length_mean

                    if self.elapsed_time + current_tumble_length\
                            < self.vars.sample_total:
                        start_vec = self.vectors_cartesian[self.elapsed_time]
                        for i in range(self.elapsed_time,
                                       self.elapsed_time
                                       + current_tumble_length):

                            if self.vars.diffusive:
                                self.vectors_cartesian[i + 1] \
                                    = Tumble(self.diffusion_sample[i],
                                             self.spin_sample[i],
                                             self.vectors_cartesian[i])
                            else:
                                self.vectors_cartesian[i + 1] = self.vectors_cartesian[i]
                            self.vectors_cartesian[i+1]\
                                = Tumble(self.vars.tumble_ang_step,
                                         self.rand_gen.uniform(0, 2*np.pi),
                                         self.vectors_cartesian[i+1])
                        self.elapsed_time += current_tumble_length
                        end_vec = self.vectors_cartesian[self.elapsed_time]
                        self.run_run_cosines.append(np.dot(start_vec, end_vec))
                        self.tumble_log.append(current_tumble_length)
                        if self.vars.chemotactic:
                            self.state = 'run_chemotactic'
                        else:
                            self.state = 'run'
                    else:
                        for i in range(self.elapsed_time,
                                       self.vars.sample_total):
                            self.vectors_cartesian[i+1] = Tumble(
                                self.diffusion_sample[i],
                                self.spin_sample[i],
                                self.vectors_cartesian[i])
                            self.tumble_log.append(
                                self.vars.sample_total-self.elapsed_time)
                        break

                # %% Smooth Tumble Mode

                elif self.state == 'smooth':

                    if self.vars.tumble_duration_mean == 0:
                        current_tumble_length = 0

                    elif self.vars.tumble_duration_variation is True:
                        current_tumble_length\
                            = int(np.ceil(self.rand_gen.exponential(
                                self.vars.tumble_length_mean)))

                    else:
                        current_tumble_length\
                            = self.vars.tumble_length_mean

                    if self.elapsed_time + current_tumble_length\
                            < self.vars.sample_total:
                        start_vec = self.vectors_cartesian[self.elapsed_time]
                        for i in range(self.elapsed_time,
                                       self.elapsed_time
                                       + current_tumble_length):

                            if self.vars.diffusive:
                                self.vectors_cartesian[i + 1] \
                                    = Tumble(self.diffusion_sample[i],
                                             self.spin_sample[i],
                                             self.vectors_cartesian[i])
                            else:
                                self.vectors_cartesian[i + 1] = self.vectors_cartesian[i]
                        self.elapsed_time += current_tumble_length
                        tumble_angle = self.vars.tumble_ang_step\
                            * current_tumble_length
                        spin_angle = self.rand_gen.uniform(0, 2*np.pi)
                        self.vectors_cartesian[self.elapsed_time]\
                            = Tumble(tumble_angle, spin_angle,
                                     self.vectors_cartesian[self.elapsed_time])
                        end_vec = self.vectors_cartesian[self.elapsed_time]
                        self.run_run_cosines.append(np.dot(start_vec, end_vec))
                        self.tumble_log.append(current_tumble_length)
                        if self.vars.chemotactic:
                            self.state = 'run_chemotactic'
                        else:
                            self.state = 'run'
                    else:
                        for i in range(self.elapsed_time,
                                       self.vars.sample_total):
                            self.vectors_cartesian[i+1] = Tumble(
                                self.diffusion_sample[i],
                                self.spin_sample[i],
                                self.vectors_cartesian[i])
                            self.tumble_log.append(
                                self.vars.sample_total-self.elapsed_time)
                        break

                # %% Pause Tumble Mode

                elif self.state == 'pause':

                    if self.vars.tumble_duration_mean == 0:
                        current_tumble_length = 0

                    elif self.vars.tumble_duration_variation is True:
                        current_tumble_length\
                            = int(np.ceil(self.rand_gen.exponential(
                                self.vars.tumble_length_mean)))

                    else:
                        current_tumble_length\
                            = self.vars.tumble_length_mean

                    if self.elapsed_time + current_tumble_length\
                            < self.vars.sample_total:
                        start_vec = self.vectors_cartesian[self.elapsed_time]
                        for i in range(self.elapsed_time,
                                       self.elapsed_time
                                       + current_tumble_length):

                            if self.vars.diffusive:
                                self.vectors_cartesian[i + 1] \
                                    = Tumble(self.diffusion_sample[i],
                                             self.spin_sample[i],
                                             self.vectors_cartesian[i])
                            else:
                                self.vectors_cartesian[i + 1] = self.vectors_cartesian[i]

                        self.elapsed_time += current_tumble_length
                        end_vec = self.vectors_cartesian[self.elapsed_time]
                        self.run_run_cosines.append(np.dot(start_vec, end_vec))
                        self.tumble_log.append(current_tumble_length)
                        if self.vars.chemotactic:
                            self.state = 'run_chemotactic'
                        else:
                            self.state = 'run'
                    else:
                        for i in range(self.elapsed_time,
                                       self.vars.sample_total):
                            self.vectors_cartesian[i+1] = Tumble(
                                self.diffusion_sample[i],
                                self.spin_sample[i],
                                self.vectors_cartesian[i])
                            self.tumble_log.append(
                                self.vars.sample_total-self.elapsed_time)
                        break

                # %% If self.state is unknown
                else:
                    print('Unknown state %s occurred at sim_time %d '
                          % (self.state, self.elapsed_time))
                    break

        # %% Rotational Diffusion simulation for non-motile samples

        else:
            for i in range(self.elapsed_time,
                           self.vars.sample_total):
                if self.vars.diffusive:
                    self.vectors_cartesian[i + 1] \
                        = Tumble(self.diffusion_sample[i],
                                 self.spin_sample[i],
                                 self.vectors_cartesian[i])
                else:
                    self.vectors_cartesian[i + 1] = self.vectors_cartesian[i]
