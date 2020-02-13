# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 22:00:16 2019

@author: henry
"""

import numpy as np
import quaternion
from scipy import constants
from scipy.spatial.transform import Rotation as R
from math import sqrt, floor, log10
from ClassLibrary import RunVars
import PyGnuplot as gp
pi = np.pi
boltz = constants.Boltzmann
avo = constants.Avogadro
g = constants.g
vec_z = np.array([0,0,1])

from numpy.random import Generator, PCG64, SeedSequence



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
    def __init__(self, runvars):
        self.seed = SeedSequence()
        self.rand_gen = Generator(PCG64(self.seed))
        self.time = np.cumsum(np.append(0.0,np.full((runvars.sample_total), runvars.base_time)))
        self.vector_initial = np.array([1,0,0])
        self.pos_initial = np.array([0,0,0])
        
    def Linear(self, runvars):
        self.std_dev_linear = 2*runvars.step_linear*sqrt(runvars.sample_steps_linear*0.25)
        self.linear_diffusion = np.random.normal(0.0, self.std_dev_linear,(runvars.sample_total, 3))
    
    def Rotational(self, runvars):
        self.std_dev_rotational = 2*runvars.step_rotational*sqrt(runvars.sample_steps_rotational*0.25)
        self.rotational_sample = self.rand_gen.normal(0.0, self.std_dev_rotational,(2, runvars.sample_total))
        self.diffusion_sample = np.sqrt(np.square(self.rotational_sample[0]) + np.square(self.rotational_sample[1]))
        self.spin_sample = np.random.random(runvars.sample_total)*2*pi
        self.vectors_cartesian = np.zeros((runvars.sample_total,3))
        self.vectors_cartesian[0] = Tumble(self.diffusion_sample[0], self.spin_sample[0], self.vector_initial)
        for i in range(1,runvars.sample_total):
            self.vectors_cartesian[i] = Tumble(self.diffusion_sample[i], self.spin_sample[i], self.vectors_cartesian[i-1])
      
    def RunTumble_Basic(self, runvars):
        vector_current = self.vector_initial
        self.displacement = np.zeros((runvars.sample_total,3))
        self.state = 0
        self.sim_time = 0
        while self.sim_time < runvars.sample_total:
            if self.state == 0 and self.sim_time+runvars.run_length <= runvars.sample_total:
                for i in range(self.sim_time, self.sim_time+runvars.run_length):
                    self.displacement[i] = vector_current*runvars.run_step
                self.sim_time = self.sim_time + runvars.run_length
                self.state=1
            elif self.state == 1 and self.sim_time+runvars.tumble_length <= runvars.sample_total:
                self.sim_time = self.sim_time + runvars.tumble_length
                tumble_spin = np.random.random()*2*pi
                vector_current = Tumble(runvars.tumble_angle_rad,tumble_spin,vector_current)
                self.state = 0
            else:
                break
        
    def Complete(self, runvars):
        self.std_dev_linear = 2*runvars.step_linear*sqrt(runvars.sample_steps_linear*0.25)
        self.linear_diffusion = self.rand_gen.normal(0.0, self.std_dev_linear,(runvars.sample_total, 3))
        self.std_dev_rotational = 2*runvars.step_rotational*sqrt(runvars.sample_steps_rotational*0.25)
        self.rotational_sample = self.rand_gen.normal(0.0, self.std_dev_rotational,(2, runvars.sample_total))
        self.diffusion_sample = np.sqrt(np.square(self.rotational_sample[0]) + np.square(self.rotational_sample[1]))
        self.spin_sample = self.rand_gen.uniform(0.0,2*pi,runvars.sample_total)
        self.vectors_cartesian = np.zeros((runvars.sample_total,3))
        self.vectors_cartesian = np.vstack((self.vector_initial, self.vectors_cartesian))
        self.displacement = np.zeros((runvars.sample_total,3))
        self.displacement += self.linear_diffusion
        self.displacement = np.vstack((self.pos_initial, self.displacement))
        self.state = 0
        self.sim_time = 0
        while self.sim_time < runvars.sample_total:
            if self.state == 0 and self.sim_time + runvars.run_length <= runvars.sample_total:
                for i in range(self.sim_time, self.sim_time+runvars.run_length):
                    self.vectors_cartesian[i+1] = Tumble(self.diffusion_sample[i],self.spin_sample[i],self.vectors_cartesian[i])
                    self.displacement[i+1] += self.vectors_cartesian[i+1]*runvars.run_step
                self.sim_time += runvars.run_length
                self.state = 1
            elif self.state == 0:
                for i in range(self.sim_time, runvars.sample_total):
                    self.vectors_cartesian[i+1] = Tumble(self.diffusion_sample[i],self.spin_sample[i],self.vectors_cartesian[i])
                    self.displacement[i+1] += self.vectors_cartesian[i+1]*runvars.run_step
                break
            elif self.state == 1 and self.sim_time + runvars.tumble_length <= runvars.sample_total:
                for i in range(self.sim_time, self.sim_time+runvars.tumble_length):
                    self.vectors_cartesian[i+1] = Tumble(self.diffusion_sample[i],self.spin_sample[i],self.vectors_cartesian[i])
                self.sim_time += runvars.tumble_length
                tumble_spin = np.random.random()*2*pi
                j = self.sim_time
                self.vectors_cartesian[j] = Tumble(runvars.tumble_angle_rad, tumble_spin, self.vectors_cartesian[j])
                self.state = 0
            elif self.state == 1:
                for i in range(self.sim_time, runvars.sample_total):
                    self.vectors_cartesian[i+1] = Tumble(self.diffusion_sample[i],self.spin_sample[i],self.vectors_cartesian[i])
                break
            else:
                print("Unknown expection occurred at sim_time = {self.sim_time}",)
                break
        self.total_displacement = np.cumsum(self.displacement, axis=0)
        
                
    def Graph_Rotational(self):
        self.graph_input = np.swapaxes(self.vectors_cartesian,0,1)
        gp.s(self.graph_input)
        gp.c('reset')
        gp.c('set ticslevel 0')
        gp.c('set view equal xyz')
        gp.c('splot "tmp.dat" u 1:2:3')

class SingleParticle_gold:
    def __init__(self, d):
        self.seed = np.random.randint(2**31-1)
        np.random.seed(self.seed)
        self.time = np.full((d.sample_total), d.base_time)

    
    def Linear(self, d):
        self.mean_linear = d.sample_steps_linear*0.5
        self.std_dev_linear = sqrt(d.sample_steps_linear*0.5*0.5)
        self.linear_sample = np.random.normal(self.mean_linear,self.std_dev_linear,(d.sample_total, 3))
        self.linear_sample -= self.mean_linear
        self.linear_sample = self.linear_sample*d.step_linear*2
        #self.linear_sample = self.linear_sample + np.tile(d.external_force_step,(d.sample_total, 1))*d.sample_steps_linear
        
        
    def Rotational(self, d):
        self.mean_rotational = 0
        self.std_dev_rotational = 0
        self.rotational_axes = np.zeros((2,d.sample_total))
        for x in range(2):
            self.mean_rotational = d.sample_steps_rotational*0.5
            self.std_dev_rotational = d.sample_steps_rotational*0.5*0.5
            self.rotational_axes[x] = np.random.normal(self.mean_rotational, self.std_dev_rotational, (1,d.sample_total))
            self.rotational_axes[x] -= self.mean_rotational
            self.rotational_axes[x] = self.rotational_axes[x]*d.step_rotational*2
        self.euler_sample = [R.from_euler('yz',(self.rotational_axes[0][x],self.rotational_axes[1][x])) for x in range(d.sample_total)]
        self.rot_curr = R.from_euler('yz',(0,0))
        self.rotational_sample = [0 for x in range(d.sample_total+1)]
        self.rotational_sample[0] = R.from_euler('yz', (0,0))
        self.vector_initial = np.array((1,0,0))
        self.vectors_cartesian = np.zeros((d.sample_total,3))
        for x in range(d.sample_total):
            self.rotational_sample[x] = self.euler_sample[x]*self.rot_curr
            self.rot_curr = self.rotational_sample[x]
            self.vectors_cartesian[x] = self.rotational_sample[x].apply(self.vector_initial)
    
    
    def RunTumble(self, d):
        self.state = 0 # 0 is Tumble, 1 is Run.
        self.run_disp = np.zeros((d.sample_total, 3))
        self.sim_time = 0
        while self.sim_time < d.sample_total:
            if self.state == 0 and self.sim_time+d.tumble_length < d.sample_total:
                self.sim_time = self.sim_time + d.tumble_length
                self.tumble_x = np.random.rand()*2*pi
                self.tumble_rot = R.from_euler('yx',(d.tumble_angle_rad, self.tumble_x))
                for x in range(int(self.sim_time), int(d.sample_total)):
                    self.vectors_cartesian[x] = self.tumble_rot.apply(self.vectors_cartesian[x])
                self.state=1
            elif self.state == 0:
                break
            elif self.state == 1 and self.sim_time+d.run_length < d.sample_total:
                for x in range (int(self.sim_time), int(self.sim_time+d.run_length)):
                    self.run_disp[x] = d.run_step*self.vectors_cartesian[x]
                self.sim_time = self.sim_time + d.run_length
                self.state = 0
            elif self.state == 1:
                for x in range (int(self.sim_time), d.sample_total):
                    self.run_disp[x] = d.run_step*self.vectors_cartesian[x]
                break
                    
        
    def Complete(self, d):
        self.Linear(d)
        self.Rotational(d)
        self.RunTumble(d)
        self.linear_output = self.linear_sample + self.run_disp
        self.linear_output = np.cumsum(self.linear_output, axis=0)
    
    def Graph_Linear_Full(self):
        self.graph_input = np.swapaxes(self.linear_output, 0,1)
        gp.s(self.graph_input)
        gp.c('splot "tmp.dat" with lines')
    
    def Graph_Rotational(self):
        self.graph_input = np.swapaxes(self.vectors_cartesian,0,1)
        gp.s(self.graph_input)
        gp.c('reset')
        gp.c('set ticslevel 0')
        gp.c('set view equal xyz')
        gp.c('splot "tmp.dat" u 1:2:3')
    
        

def LinearDiffusionAnalysis(z,d):
    linear = np.cumsum(z.linear_sample, axis=0)
    tau = d.base_time
    sample_total = floor(np.log2(d.run_time/d.base_time))
    results = [np.zeros(sample_total) for x in range(3)]
    run_total = d.sample_total
    for i in range(sample_total):
        results[2][i] = tau
        sample_size = floor(d.run_time/tau)
        tau_i = floor(run_total/sample_size)
        for y in range(3):
            results_stack = np.zeros(sample_size-1)
            for x in range(sample_size-1):
                results_stack[x] = linear[(x+1)*tau_i][y]-linear[x*tau_i][y]
            results_stack_2 = results_stack**2
            results[0][i] = results[0][i] + np.mean(results_stack_2)
        tau = tau*2
    results[1] = results[2]*6*d.diffusion_constant_linear
    gp.s(results)
    gp.c('reset')
    gp.c('set logscale xy 10')
    gp.c('set xlabel "{/Symbol t} (s)"')
    gp.c('set ylabel "MSD (m^2)"')
    gp.c('set title "Analysis of Linear Diffusion Mean Squared Displacement"')
    gp.c('plot "tmp.dat" u 3:1 w points title "Actual MSD", "tmp.dat" u 3:2 w lines title "Expected MSD"')


def RotationalAnalysis(z,d, graph=True):
    rotational_vect = z.vectors_cartesian
    tau = d.base_time
    sample_total = floor(np.log2(d.run_time/d.base_time))
    results = [np.zeros(sample_total) for x in range(3)]
    run_total = d.sample_total
    for i in range(sample_total):
        results[2][i] = tau
        sample_size = floor(d.run_time/tau)
        tau_i = floor(run_total/sample_size)
        results_stack = np.zeros(sample_size-1)
        for x in range(sample_size-1):
            results_stack[x] = np.dot(rotational_vect[(x+1)*tau_i],rotational_vect[x*tau_i])
            results_stack[x] = np.arccos(results_stack[x])
        results_stack_2 = results_stack**2
        results[0][i] = np.mean(results_stack_2)
        tau = tau*2
    results[1] = results[2]*4*d.diffusion_constant_rotational
    gp.s(results)
    gp.c('reset')
    gp.c('set logscale xy 10')
    gp.c('set xlabel "{/Symbol t} (s)"')
    gp.c('set ylabel "MSD ({/Symbol q}^2)"')
    gp.c('set title "Analysis of Rotational Diffusion Mean Squared Displacement"')
    gp.c('plot "tmp.dat" u 3:1 w points title "Actual MSD", "tmp.dat" u 3:2 w lines title "Expected MSD"')
    
    
    


    
    
    
    