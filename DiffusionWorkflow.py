# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 20:07:28 2019

@author: henry

TODO: Make sure units are consistant
"""

import numpy as np
from math import sqrt, ceil
import datetime
import os
from scipy import constants

pi = np.pi
boltz = constants.Boltzmann
avo = constants.Avogadro
g = constants.g


        
        

def Diffusion(molecular_mass, temperature, absolute_viscosity, radius, particles, external_force, gravity, run_time, intermediate_time, base_time):
    
    if type(radius) == float :
        frictional_drag_linear = 6*pi*absolute_viscosity*radius
        frictional_drag_rotational = 8*pi*absolute_viscosity*(radius**3)
    elif type(radius) == tuple :
        q = np.log(2*radius[0]/radius[1])
        frictional_drag_linear = 6*pi*absolute_viscosity*radius[0]/q
        frictional_drag_rotational = (8*pi*absolute_viscosity*(radius**3)/3)/(q+0.5)
    else:
        print("Error: Invalid Datatype for radius")
        return 0

    diffusion_constant_linear = temperature*boltz/frictional_drag_linear
    diffusion_constant_rotational = temperature*boltz/frictional_drag_rotational
    particle_mass = molecular_mass/avo
    rms_velocity = sqrt(boltz*temperature/particle_mass)
    step_linear = 2*diffusion_constant_linear/rms_velocity
    step_rate = rms_velocity/step_linear
    step_time = 1.0/step_rate
    step_rotational = sqrt(2*step_time*diffusion_constant_rotational)

    external_force = np.asarray(external_force)
    external_acceleration = external_force/particle_mass
    if gravity == 1:
        external_acceleration = external_acceleration+np.asarray((0,0,-g))
    external_force_step = external_acceleration*0.5*step_time**2

    sample_total = ceil(run_time/base_time)
    sample_steps = ceil(step_rate*base_time/2)*2
    sample_time = step_time*sample_steps

    intermediate_total = ceil(run_time/intermediate_time)
    intermediate_sample = ceil(intermediate_time/base_time)

    results = np.zeros((particles,intermediate_total, 7))

    for x in range(particles):
        seed = np.zeros((intermediate_total,1), dtype=int)
        particle_results = np.zeros((intermediate_total,6))
        for y in range(intermediate_total):
            seed[y] = np.random.randint(2**31-1)
            np.random.seed(seed[y])

            linear_sample = np.random.binomial(sample_steps, 0.5, (intermediate_sample,3))
            linear_sample = linear_sample-(sample_steps*0.5)
            linear_sample = linear_sample*step_linear
            linear_sample = linear_sample + np.tile(external_force_step,(intermediate_sample,1))*sample_steps

            rotational_sample = np.random.binomial(sample_steps, 0.5, (intermediate_sample,2))
            rotational_sample = rotational_sample-(sample_steps*0.5)
            rotational_sample = rotational_sample*step_rotational
            #return rotational_sample
            time = np.full((intermediate_sample,1), sample_time)

            diffusion = np.hstack((linear_sample,rotational_sample,time))
            #return np.sum(diffusion, axis=0)
            particle_results[y] = np.sum(diffusion, axis=0)

        results[x] = np.hstack((particle_results,seed))
    render_variables = np.asarray((sample_steps,intermediate_sample,step_linear,step_rotational,sample_time))
    input_variables = np.asarray((molecular_mass, temperature, absolute_viscosity, radius, particles, external_force, gravity, run_time, intermediate_time, base_time))
    
    i = 0
    while os.path.exists("LinearDiffusion "+str(datetime.date.today())+" "+str(i)+".npz"):
        i = i+1
    
    fileName = "LinearDiffusion "+str(datetime.date.today())+" "+str(i)+".npz"
    np.savez(fileName, results=results, render_variables=render_variables, input_variables=input_variables)

    return results, render_variables, input_variables

#def DiffusionRender(input_value="", time_span="", particles=""):
#    input_array = input_tuple(0)
#    if particles == "":
#        render_array = input_array
#        particle_number = len(results)
#    elif type(particles)==int:
#        render_array = np.zeros()
#        particle_number=1
#    elif type(particles)==list:
#        render_array = np.vsplit([particles[0]]
#        for x in range(1, len(particles)):
#            render_array = np.vstack(render_array,input_array)
#    results,seed = np.dsplit(input_array,[6])
#    time_start = time_span[0]
#    time_end = time_span[1]
