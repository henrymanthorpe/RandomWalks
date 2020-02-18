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

vec_z = np.array([0,0,1])
pi = np.pi

def Normalise(vec):
    return vec/np.linalg.norm(vec)

def MakeRotationQuaternion(angle, vec):
    a = np.cos(angle/2)
    b = np.sin(angle/2)
    axis = vec*b
    axis = np.append(a,axis)
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

class Bacterium:
    def __init__(self, fname):
        self.vars = Variables(fname)
        if self.vars.success == 1:
            return 1
        self.seed = SeedSequence()
        self.rand_gen = Generator(PCG64(self.seed))
        #self.time = np.cumsum(np.append(0.0,np.full((self.vars.sample_total), self.vars.base_time)))
        self.vector_initial = np.array([1,0,0])
        self.pos_initial = np.array([0,0,0])
    
    def ReSeed(self,entropy):
        self.seed = SeedSequence(entropy)
        self.rand_gen = Generator(PCG64(self.seed))

    def Linear(self):
        self.std_dev_linear = 2*self.vars.step_linear*np.sqrt(self.vars.sample_steps_linear*0.25)
        self.linear_diffusion = np.random.normal(0.0, self.std_dev_linear,(self.vars.sample_total, 3))
    
    def Rotational(self):
        self.std_dev_rotational = 2*self.vars.step_rotational*np.sqrt(self.vars.sample_steps_rotational*0.25)
        self.rotational_sample = self.rand_gen.normal(0.0, self.std_dev_rotational,(2, self.vars.sample_total))
        self.diffusion_sample = np.sqrt(np.square(self.rotational_sample[0]) + np.square(self.rotational_sample[1]))
        self.spin_sample = np.random.random(self.vars.sample_total)*2*pi
        self.vectors_cartesian = np.zeros((self.vars.sample_total,3))
        self.vectors_cartesian[0] = Tumble(self.diffusion_sample[0], self.spin_sample[0], self.vector_initial)
        for i in range(1,self.vars.sample_total):
            self.vectors_cartesian[i] = Tumble(self.diffusion_sample[i], self.spin_sample[i], self.vectors_cartesian[i-1])
        
    def Complete(self):
        self.std_dev_linear = 2*self.vars.step_linear*np.sqrt(self.vars.sample_steps_linear*0.25)
        self.linear_diffusion = self.rand_gen.normal(0.0, self.std_dev_linear,(self.vars.sample_total, 3))
        self.std_dev_rotational = 2*self.vars.step_rotational*np.sqrt(self.vars.sample_steps_rotational*0.25)
        self.rotational_sample = self.rand_gen.normal(0.0, self.std_dev_rotational,(2, self.vars.sample_total))
        self.diffusion_sample = np.sqrt(np.square(self.rotational_sample[0]) + np.square(self.rotational_sample[1]))
        self.spin_sample = self.rand_gen.uniform(0.0,2*pi,self.vars.sample_total)
        self.vectors_cartesian = np.zeros((self.vars.sample_total,3))
        self.vectors_cartesian = np.vstack((self.vector_initial, self.vectors_cartesian))
        self.displacement = np.zeros((self.vars.sample_total,3))
        self.displacement += self.linear_diffusion
        self.displacement = np.vstack((self.pos_initial, self.displacement))
        self.state = 0
        self.elapsed_time = 0
        p = 0
        q = 0
        self.run_tumble_log = {}
        if self.vars.run_behaviour == True:
            while self.elapsed_time < self.vars.sample_total:
                if self.state == 0:
                    p += 1
                    if self.vars.run_variation == True:
                        current_run_length = int(np.round(self.rand_gen.exponential(self.vars.run_length_mean)))
                    else:
                        current_run_length = self.vars.run_length_mean
                    if self.elapsed_time + current_run_length <= self.vars.sample_total:
                        for i in range(self.elapsed_time, self.elapsed_time+current_run_length):
                            self.vectors_cartesian[i+1] = Tumble(self.diffusion_sample[i],self.spin_sample[i],self.vectors_cartesian[i])
                            self.displacement[i+1] += self.vectors_cartesian[i+1]*self.vars.run_step
                        self.elapsed_time += current_run_length
                        self.run_tumble_log['run'+str(p)] = current_run_length
                        self.state = 1
                    else:
                        for i in range(self.elapsed_time, self.vars.sample_total):
                            self.vectors_cartesian[i+1] = Tumble(self.diffusion_sample[i],self.spin_sample[i],self.vectors_cartesian[i])
                            self.displacement[i+1] += self.vectors_cartesian[i+1]*self.vars.run_step
                            self.run_tumble_log['run'+str(p)] = self.vars.sample_total-self.elapsed_time
                        break
                elif self.state == 1:
                    q += 1
                    if self.vars.tumble_behaviour == True:
                        if self.vars.tumble_duration_variation == True:
                            current_tumble_length = int(np.round(self.rand_gen.exponential(self.vars.tumble_length_mean)))
                        else:
                            current_tumble_length = self.vars.tumble_length_mean
                    if self.elapsed_time + current_tumble_length <= self.vars.sample_total:
                        for i in range(self.elapsed_time, self.elapsed_time+self.vars.tumble_length_mean):
                            self.vectors_cartesian[i+1] = Tumble(self.diffusion_sample[i],self.spin_sample[i],self.vectors_cartesian[i])
                        self.elapsed_time += self.vars.tumble_length_mean
                        tumble_spin = np.random.random()*2*pi
                        j = self.elapsed_time
                        self.vectors_cartesian[j] = Tumble(self.vars.tumble_angle_mean, tumble_spin, self.vectors_cartesian[j])
                        self.run_tumble_log['tumble'+str(q)] = current_tumble_length
                        self.state = 0
                    else:
                        for i in range(self.elapsed_time, self.vars.sample_total):
                            self.vectors_cartesian[i+1] = Tumble(self.diffusion_sample[i],self.spin_sample[i],self.vectors_cartesian[i])
                            self.run_tumble_log['tumble'+str(q)] = self.vars.sample_total-self.elapsed_time
                            
                        break
                else:
                    print("Unknown expection occurred at sim_time = {self.elapsed_time}",)
                    break
        self.total_displacement = np.cumsum(self.displacement, axis=0)