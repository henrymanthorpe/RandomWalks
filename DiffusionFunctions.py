# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 22:00:16 2019

@author: henry
"""

import numpy as np
from scipy import constants
from scipy.spatial.transform import Rotation as R
from math import sqrt, ceil, floor, log10, cos, sin
from matplotlib import pyplot as plt
from ClassLibrary import RunVars
import PyGnuplot as gp
pi = np.pi
boltz = constants.Boltzmann
avo = constants.Avogadro
g = constants.g


class SingleParticle:
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
        self.mean_rotational = np.zeros(3)
        self.std_dev_rotational = np.zeros(3)
        self.rotational_axes = np.zeros((3,d.sample_total))
        for x in range(3):
            self.mean_rotational[x] = d.sample_steps_rotational[x]*0.5
            self.std_dev_rotational[x] = d.sample_steps_rotational[x]*0.5*0.5
            self.rotational_axes[x] = np.random.normal(self.mean_rotational[x], self.std_dev_rotational[x], (1,d.sample_total))
            self.rotational_axes[x] -= self.mean_rotational[x]
            self.rotational_axes[x] = self.rotational_axes[x]*d.step_rotational[x]*2
        self.euler_sample = [R.from_euler('xyz',(self.rotational_axes[0][x],self.rotational_axes[1][x],self.rotational_axes[2][x])) for x in range(d.sample_total)]
        self.rot_curr = R.from_euler('xyz',(0,0,0))
        self.rotational_sample = [0 for x in range(d.sample_total+1)]
        self.rotational_sample[0] = R.from_euler('xyz', (0,0,0))
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
                self.tumble_rot = R.from_euler('xyx',(self.tumble_x, d.tumble_angle_rad, -self.tumble_x))
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
        gp.c('splot "tmp.dat" u 1:2:3')
    
        

def SingleParticleAnalysis(z,d, graph=True):
    linear = np.cumsum(z.linear_sample, axis=1)
    tau = d.base_time
    sample_total = floor(log10(d.run_time/d.base_time))
    results = [np.zeros(sample_total) for x in range(4)]
    run_total = len(z.time)
    for i in range(sample_total):
        results[3][i] = tau
        sample_size = floor(d.run_time/tau)
        tau_i = floor(run_total/sample_size)
        for y in range(3):
            results_stack = np.zeros(sample_size)
            for x in range(sample_size-1):
                results_stack[x] = linear[y][(x+1)*tau_i]-linear[y][x*tau_i]
            results_stack_2 = results_stack**2
            results[y][i] = np.mean(results_stack_2)
        tau = tau*10
        
    if graph==False:
        return results
    else:
        labels = ['x','y','z']
        expected_msd = results[3]*2*d.diffusion_constant_linear
        for x in range(3):
            plt.title("Expected vs Actual MSD - {label}".format(label=labels[x]))
            plt.xlabel("Tau (s)")
            plt.ylabel("{label}^2 (m^2)".format(label=labels[x]))
            plt.xscale("log")
            plt.yscale("log")
            plt.plot(results[3], results[x], 'r-', results[3], expected_msd, 'b-')
            plt.show()
            
        return results
            
        
    
    
def SingleParticleFull():
    x = RunVars()
    x.Build()
    z = SingleParticle(x)
    SingleParticleAnalysis(z,x)
    
def MultiParticleDiffusion(particle_total, d):
    particles = [ 0 for x in range(particle_total)]
    for x in range(particle_total):
        particles[x] = SingleParticle(d)
        particles[x].Linear(d)
    return particles

def MultiParticleAnalysis(z,d):
    results = [SingleParticleAnalysis(z[x],d,graph=False) for x in range(len(z))]
    labels = ['x','y','z']
    expected_msd = 2*d.diffusion_constant_linear*results[0][3]
    for x in range(3):
        plt.title("Expected vs Actual MSD - {label}".format(label=labels[x]))
        plt.xlabel("Tau (s)")
        plt.ylabel("{label}^2 (m^2)".format(label=labels[x]))
        plt.xscale("log")
        plt.yscale("log")
        for y in range(len(z)):
            plt.plot(results[y][3], results[y][x], 'r-')
        plt.plot(results[y][3], expected_msd, 'b-')
        plt.show()
    return results


    
    
    
    