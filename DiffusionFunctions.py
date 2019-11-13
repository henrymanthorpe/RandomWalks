# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 22:00:16 2019

@author: henry
"""

import numpy as np
from scipy import constants
from scipy.spatial.transform import Rotation as R
from math import sqrt
from matplotlib import pyplot as plt
from ClassLibrary import RunVars, DiffVars, Particle
pi = np.pi
boltz = constants.Boltzmann
avo = constants.Avogadro
g = constants.g


class DiffusionIntermediate:
    def __init__(self, d):
        self.seed = np.random.randint(2**31-1)
        np.random.seed(self.seed)
        self.mean = d.sample_steps*0.5
        self.std_dev = sqrt(d.sample_steps*0.5*0.5)
        self.linear_sample = np.random.normal(self.mean,self.std_dev,(d.intermediate_sample,3))
        self.linear_sample = self.linear_sample -self.mean
        self.linear_sample = self.linear_sample*d.step_linear*2
        self.linear_sample = self.linear_sample + np.tile(d.external_force_step,(d.intermediate_sample,1))*d.sample_steps
        
        self.rotational_sample = np.random.normal(self.mean,self.std_dev,(d.intermediate_sample,3))
        self.rotational_sample = self.rotational_sample - self.mean
        self.rotational_sample = self.rotational_sample*d.step_rotational*2
        
        self.euler_sample = [R.from_euler('xyz', self.rotational_sample[x]) for x in range(d.intermediate_sample)]
        self.rot_curr = R.from_euler('xyz', (0,0,0))
        for x in range(d.intermediate_sample):
            self.euler_sample[x] = self.euler_sample[x]*self.rot_curr
            self.rot_curr = self.euler_sample[x]
        
        self.time = np.full((d.intermediate_sample, 1), d.sample_time)
     
class SingleParticleDiffusion:
    def __init__(self, d):
        self.linear_result = np.zeros((d.intermediate_total, 3))
        self.rotational_result = [0 for x in range(d.intermediate_total)]
        self.rotational_total = np.zeros((d.intermediate_total, 3))
        self.seed = np.zeros((d.intermediate_total, 1))
        for x in range(d.intermediate_total):
            current_result = DiffusionIntermediate(d)
            self.linear_result[x] = np.sum(current_result.linear_sample, axis=0)
            self.rotational_result[x] = current_result.rot_curr
            self.rotational_total[x] = np.sum(current_result.rotational_sample, axis=0)
            self.seed[x] = current_result.seed
            

def SingleParticleAnalysis(z, d):
    diffusion_2 = z.linear_result**2
    displacement_2 = np.cumsum(diffusion_2, axis=0)
    actual_r_2 = np.sum(displacement_2, axis=1)
    time = np.cumsum(np.full((d.intermediate_total,1), d.sample_time*d.intermediate_sample))
    expected_r_2 = 6*d.diffusion_constant_linear*time
    plt.title("Expected vs Actual MSD")
    plt.xlabel("Time (s)")
    plt.ylabel("r^2 (m^2)")
    plt.plot(time, actual_r_2, 'r-', time, expected_r_2, 'b-')
    plt.show()
    rotation = np.array([z.rotational_result[x].as_euler('xyz') for x in range(d.intermediate_total)])
    rotation_2 = rotation**2
    rotation_2 = np.cumsum(rotation_2, axis = 0)
    actual_rotation_2 = [0,0,0]
    actual_rotation_2[0],actual_rotation_2[1],actual_rotation_2[2] = np.hsplit(rotation_2, 3)
    expected_rotation_2 = [2*d.diffusion_constant_rotational[x]*time for x in range(3)]
    other_rotation_2 = z.rotational_total**2
    other_rotation_2 = np.cumsum(other_rotation_2, axis = 0)
    fake_rotation_2 = [0,0,0]
    fake_rotation_2[0],fake_rotation_2[1],fake_rotation_2[2] = np.hsplit(other_rotation_2, 3)
    
    labels = ['x','y','z']
    for x in range(3):
        plt.xlabel("Time (s)")
        plt.ylabel("theta({label})^2 (radians^2)".format(label=labels[x]))
        plt.plot(time, actual_rotation_2[x], 'r-', time, expected_rotation_2[x], 'b-', time, fake_rotation_2[x],'g-')
        plt.show()
        
    
def SingleParticleFull():
    x = RunVars()
    x.Build()
    y = DiffVars(x)
    z = SingleParticleDiffusion(y)
    SingleParticleAnalysis(z,y)
    
def MultiParticleDiffusion(particle_total, d):
    particles = [Particle(d) for x in range(particle_total)]
    for x in range(particle_total):
        for y in range(d.intermediate_total):
            current_result = DiffusionIntermediate(d)
            particles[x].linear_dis[y] = np.sum(current_result.linear_sample, axis=0)
            particles[x].seed[y] = current_result.seed
    return particles

def MultiParticleAnalysis(particles, d):
    total_r_2 = np.zeros((d.intermediate_total))
    total_diff_2 = np.zeros((d.intermediate_total,3))
    for x in range(len(particles)):
        disp_2 = particles[x].linear_dis**2
        diff_2 = np.cumsum(disp_2, axis=0)
        total_diff_2 += diff_2
        r_2 = np.sum(diff_2, axis=1)
        total_r_2 += r_2
    mean_r_2 = total_r_2/len(particles)
    mean_diff_2 = total_diff_2/len(particles)
    mean_x_2, mean_y_2, mean_z_2 = np.hsplit(mean_diff_2, 3)
    time = np.cumsum(np.full((d.intermediate_total), d.sample_time*d.intermediate_sample))
    expected_r_2 = 6*d.diffusion_constant_linear*time
    expected_x_2 = 2*d.diffusion_constant_linear*time
    plt.title("Expected vs Actual MSD - x^2")
    plt.xlabel("Time (s)")
    plt.ylabel("r^2 (m^2)")
    plt.plot(time, mean_x_2, 'r-', time, expected_x_2, 'b-')
    plt.show()
    plt.title("Expected vs Actual MSD - y^2")
    plt.xlabel("Time (s)")
    plt.ylabel("r^2 (m^2)")
    plt.plot(time, mean_y_2, 'r-', time, expected_x_2, 'b-')
    plt.show()
    plt.title("Expected vs Actual MSD - z^2")
    plt.xlabel("Time (s)")
    plt.ylabel("r^2 (m^2)")
    plt.plot(time, mean_z_2, 'r-', time, expected_x_2, 'b-')
    plt.show()
    plt.title("Expected vs Actual MSD - r^2")
    plt.xlabel("Time (s)")
    plt.ylabel("r^2 (m^2)")
    plt.plot(time, mean_r_2, 'r-', time, expected_r_2, 'b-')
    plt.show()
    
        
        
    
    
    
    
    
    