# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 21:38:37 2019

@author: henry
"""

import numpy as np
from scipy import constants
from math import sqrt, ceil

pi = np.pi
boltz = constants.Boltzmann
avo = constants.Avogadro
g = constants.g

class RunVars:
    
    def __init__(self):
        self.absolute_viscosity=0
        self.base_time=0
        self.external_forces=(0,0,0)
        self.intermediate_time=0
        self.molecular_mass=0
        self.radius=0
        self.run_time=0
        self.temperature=0
        
    def Define(self, molecular_mass, temperature, absolute_viscosity, radius, external_forces, run_time, intermediate_time, base_time):
        self.absolute_viscosity=absolute_viscosity
        self.base_time=base_time
        self.external_forces=external_forces
        self.intermediate_time=intermediate_time
        self.molecular_mass=molecular_mass
        self.radius=radius
        self.run_time=run_time
        self.temperature=temperature
    
    def Build(self):
        print("Welcome to the guided Variable builder \n")
        print("--- Particle Variables ---")
        while True:
            try:
                self.molecular_mass = float(input("Input molecular mass of the particle (kg/mol) :"))
                if self.molecular_mass > 0:
                    break
                else:
                    print("Error: Negative Mass not possible")
            except ValueError:
                print("Error: That is not a numerical input")
        
        while True:
            try:
                self.particle_shape = input("Select particle shape - (S)phere or (E)llipsoid : ")
                if self.particle_shape == 'E' or self.particle_shape.lower()=='ellipsoid':
                    self.radius = list([0,0])
                    while True:
                        try:
                            self.radius[0] = float(input("Input semi-major axis (m) : "))
                            if self.radius[0] > 0:
                                break
                            else:
                                print("Error: Negative value not possible")
                        except ValueError:
                            print("Error: That is not a numerical input")
                    while True:
                        try:
                            self.radius[1] = float(input("Input semi-minor axis (m) : "))
                            if self.radius[1] > 0:
                                break
                            else:
                                print("Error: Negative value not possible")
                        except ValueError:
                            print("Error: That is not a numerical input")
                    break
                
                elif self.particle_shape == 'S' or self.particle_shape.lower()=='sphere':
                    while True:
                        try:
                            self.radius = float(input("Input spherical radius (m) : "))
                            if self.radius > 0:
                                break
                            else:
                                print("Error: Negative value not possible")
                        except ValueError:
                            print("Error: That is not a numerical input")
                    break
                    
                else:
                    print("Error:Not a valid input")
            except SyntaxError:
                print("Error: That is not an allowed input")
            
        print("\n--System Variables--")
        while True:
            try:
                self.temperature = float(input("Input absolute temperature (K) : "))
                if self.temperature > 0:
                    break
                else:
                    print("Error: Negative value not possible")
            except ValueError:
                print("Error: That is not a numerical input")
        while True:
            try:
                self.absolute_viscosity = float(input("Input absolute viscosity kg/(m*s) : "))
                if self.absolute_viscosity > 0:
                    break
                else:
                    print("Error: Negative value not possible")
            except ValueError:
                print("Error: That is not a numerical input")
        
        while True:
            try:
                self.force_input = input("Input external forces (x,y,z) (N) : ")
                self.external_forces = np.asarray(self.force_input.split(','), dtype=float)
                if len(self.external_forces.shape) == 1 and self.external_forces.shape[0]==3:
                    break
                else:
                    print("Error: Requires three inputs")
            except ValueError:
                print("Error: That is not a numerical input")
        print("\n--Time Variables--")
        while True:
            try:
                self.run_time = float(input("Input run time (s) : "))
                if self.run_time > 0:
                    break
                else:
                    print("Error: Negative value not possible")
            except ValueError:
                print("Error: That is not a numerical input")
        while True:
            try:
                self.intermediate_time = float(input("Input intermediate time (s) : "))
                if self.intermediate_time > 0:
                    break
                else:
                    print("Error: Negative value not possible")
            except ValueError:
                print("Error: That is not a numerical input")
        while True:
            try:
                self.base_time = float(input("Input base time (s) : "))
                if self.base_time > 0:
                    break
                else:
                    print("Error: Negative value not possible")
            except ValueError:
                print("Error: That is not a numerical input")

class DiffVars:
    def __init__(self, v): #v is a RunVars object
        self.diffusion_constant_rotational = np.zeros(3)
        if type(v.radius) == float :
            self.frictional_drag_linear = 6*pi*v.absolute_viscosity*v.radius
            self.frictional_drag_rotational = 8*pi*v.absolute_viscosity*(v.radius**3)
            self.diffusion_constant_rotational[0] = v.temperature*boltz/self.frictional_drag_rotational
            self.diffusion_constant_rotational[1] = v.temperature*boltz/self.frictional_drag_rotational
            self.diffusion_constant_rotational[2] = v.temperature*boltz/self.frictional_drag_rotational
        elif type(v.radius) == list :
            q = np.log(2*v.radius[0]/v.radius[1])
            self.frictional_drag_linear = 6*pi*v.absolute_viscosity*v.radius[0]/q
            self.frictional_drag_rotational_minor = (8*pi*v.absolute_viscosity*(v.radius[0]**3)/3)/(q+0.5)
            self.frictional_drag_rotational_major = (16/3)*pi*v.absolute_viscosity*v.radius[0]*v.radius[1]**2
            self.diffusion_constant_rotational[0] = v.temperature*boltz/self.frictional_drag_rotational_major
            self.diffusion_constant_rotational[1] = v.temperature*boltz/self.frictional_drag_rotational_minor
            self.diffusion_constant_rotational[2] = v.temperature*boltz/self.frictional_drag_rotational_minor
        else:
            print("Error: Invalid Datatype for radius")
            return 0
        
        self.diffusion_constant_linear = v.temperature*boltz/self.frictional_drag_linear
        self.particle_mass = v.molecular_mass/avo
        self.rms_velocity = sqrt(boltz*v.temperature/self.particle_mass)
        self.step_linear = 2*self.diffusion_constant_linear/self.rms_velocity
        self.step_rate = self.rms_velocity/self.step_linear
        self.step_time = 1.0/self.step_rate
        self.step_rotational = np.sqrt(2*self.step_time*self.diffusion_constant_rotational)
        self.external_acceleration = v.external_forces/self.particle_mass
        self.external_force_step = self.external_acceleration*0.5*self.step_time**2
        self.sample_total = ceil(v.run_time/v.base_time)
        self.sample_steps = self.step_rate*v.base_time
        self.sample_time = self.step_time*self.sample_steps
        self.intermediate_total = ceil(v.run_time/v.intermediate_time)
        self.intermediate_sample = ceil(v.intermediate_time/v.base_time)

class Particle:
    def __init__(self, v):
        self.linear_dis = np.zeros((v.intermediate_total,3))
        self.rotational_dis = [x for x in range(v.intermediate_total)]
        self.unit_vector = np.zeros((v.intermediate_total,3))
        self.seed = np.zeros((v.intermediate_total,1),dtype=int)
        self.run = 0