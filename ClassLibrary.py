# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 21:38:37 2019

@author: henry
"""

import numpy as np
from scipy import constants
from math import sqrt, ceil
import os
import datetime

pi = np.pi
boltz = constants.Boltzmann
avo = constants.Avogadro
g = constants.g

class RunVars:
    # Holds User-defined Variables for Particle Simulations

    def __init__(self):
        self.absolute_viscosity=0
        self.temperature=0
        self.external_forces=(0,0,0)
        self.molecular_mass=0
        self.radius=0
        self.run_time=0
        self.base_time=0
        self.run_speed=0
        self.run_duration=0
        self.tumble_angle_deg=0
        self.tumble_duration=0


    def Build(self):

        self.diffusion_constant_rotational = 0
        if type(self.radius) == float :
            self.frictional_drag_linear = 6*pi*self.absolute_viscosity*self.radius
            self.frictional_drag_rotational = 8*pi*self.absolute_viscosity*(self.radius**3)
            self.diffusion_constant_rotational = self.temperature*boltz/self.frictional_drag_rotational
        

        # elif type(self.radius) == list :
        #     q = np.log(2*self.radius[0]/self.radius[1])
        #     self.frictional_drag_linear = 6*pi*self.absolute_viscosity*self.radius[0]/q
        #     self.frictional_drag_rotational_minor = (8*pi*self.absolute_viscosity*(self.radius[0]**3)/3)/(q+0.5)
        #     self.diffusion_constant_rotational = self.temperature*boltz/self.frictional_drag_rotational_minor
            
        else:
            print("Error: Invalid Datatype for radius")
            return 1
        
        self.diffusion_constant_linear = self.temperature*boltz/self.frictional_drag_linear
        self.particle_mass = self.molecular_mass/avo
        self.MoI = 0.4*self.particle_mass*self.radius**2
        self.rms_velocity_linear = sqrt(boltz*self.temperature/self.particle_mass)
        self.rms_velocity_rotational = sqrt(boltz*self.temperature/self.MoI)
        self.step_linear = 2*self.diffusion_constant_linear/self.rms_velocity_linear
        self.step_rate_linear = self.rms_velocity_linear/self.step_linear
        self.step_time_linear = 1.0/self.step_rate_linear
        self.external_forces = self.external_forces.reshape(3,1)
        self.external_acceleration = self.external_forces/self.particle_mass
        self.external_force_step = self.external_acceleration*0.5*self.step_time_linear**2
        self.sample_total = ceil(self.run_time/self.base_time)
        self.run_time = self.base_time*self.sample_total #Increases run_time to include integer number of samples
        self.sample_steps_linear = self.step_rate_linear*self.base_time
        self.step_rotational = 2*self.diffusion_constant_rotational/self.rms_velocity_rotational
        self.step_rate_rotational = self.rms_velocity_rotational/self.step_rotational
        self.step_time_rotational = 1.0/self.step_rate_rotational
        self.sample_steps_rotational = self.step_rate_rotational*self.base_time
        # Build for basic fixed run&tumble
        self.run_length = np.round((self.run_duration/self.base_time))
        self.tumble_length = np.round((self.tumble_duration/self.base_time))
        self.run_step = self.run_speed*self.base_time
        self.tumble_angle_rad = np.deg2rad(self.tumble_angle_deg)

    def Input(self):
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
                self.particle_shape = input("Select particle shape - (S)phere or (E)llipsoid (ELLIPSOIDS CURRENTLY DON'T WORK) : ")
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
                self.base_time = float(input("Input base time (s) : "))
                if self.base_time > 0:
                    break
                else:
                    print("Error: Negative value not possible")
            except ValueError:
                print("Error: That is not a numerical input")
        print("\n--Run&Tumble Variables--")
        while True:
            try:
                self.run_speed = float(input("Input average run speed (m/s) : "))
                if self.run_speed > 0:
                    break
                else:
                    print("Error: Negative value not possible")
            except ValueError:
                print("Error: That is not a numerical input")
        while True:
            try:
                self.run_duration = float(input("Input average run duration (s) : "))
                if self.run_duration > 0:
                    break
                else:
                    print("Error: Negative value not possible")
            except ValueError:
                print("Error: That is not a numerical input")
        while True:
            try:
                self.tumble_angle_deg = float(input("Input average tumble angle (degrees) : "))
                if self.tumble_angle_deg >= 0 and self.tumble_angle_deg <= 360:
                    break
                else:
                    print("Error: Please input value between 0 and 360 inclusive")
            except ValueError:
                print("Error: That is not a numerical input")
        while True:
            try:
                self.tumble_duration = float(input("Input average tumble duration (s) : "))
                if self.tumble_duration > 0:
                    break
                else:
                    print("Error: Negative value not possible")
            except ValueError:
                print("Error: That is not a numerical input")
        self.Build()

    def Save(self, f_name = ''):
        if f_name == '':
            i = 0
            while os.path.exists("RunVariables "+str(datetime.date.today())+" "+str(i)+".npy"):
                i = i+1

            f_name = "RunVariables "+str(datetime.date.today())+" "+str(i)
        elif type(f_name) != str:
            print("Error: File name must be a string")
            return 1
        out_list = [self.base_time,self.run_time,self.absolute_viscosity,self.temperature,self.external_forces,self.molecular_mass, self.radius, self.run_speed, self.run_duration, self.tumble_angle_deg, self.tumble_duration]
        out_array = np.array(out_list)
        np.save(f_name, out_array)
        return 0

    def Load(self, f_name):
        f_name = f_name + ".npy"
        in_array = np.load(f_name, allow_pickle=True)
        self.base_time=in_array[0]
        self.run_time=in_array[1]
        self.absolute_viscosity=in_array[2]
        self.temperature=in_array[3]
        self.external_forces=in_array[4]
        self.molecular_mass=in_array[5]
        self.radius=in_array[6]
        self.run_speed=in_array[7]
        self.run_duration=in_array[8]
        self.tumble_angle_deg=in_array[9]
        self.tumble_duration=in_array[10]
        self.Build()
