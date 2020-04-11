#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 22:04:35 2020

@author: henry
"""
import Config
import numpy as np
from scipy import constants
import os
import sys


def waterViscosityPoling(T):
    A = 1.856e-11
    B = 4209
    C = 0.04527
    D = -3.376e-5
    return A*np.exp((B/T)+C*T+D*T**2)*1e-3


class Variables:

    def __init__(self, fname):
        tumble_states = ['smooth', 'erratic', 'pause']
        chem_styles = ['linear']
        pi = np.pi
        boltz = constants.Boltzmann
        avo = constants.Avogadro
        try:

            config = Config.GetConfig(fname)
            if config.sections() == ['name', 'phys', 'env', 'time', 'bact',
                                     'chem', 'seed']:
                self.name = config['name'].get('name')
                self.phys = config['phys']
                self.env = config['env']
                self.time = config['time']
                self.bact = config['bact']
                self.chem = config['chem']
                self.entropy = config['seed'].get('entropy')
            else:
                print('Error: Config file not formatted correctly.')
                print('Please recreate options'
                      + ' from default config and try again.')
                raise ValueError()
            if not self.name:
                self.name = os.path.splitext(os.path.split(fname)[1])[0]
            self.viscosity = self.env.get('viscosity')
            self.temperature = self.env.getfloat('temp')
            if self.viscosity == 'water':
                if 272.9 < self.temperature <= 373.0:
                    self.viscosity = waterViscosityPoling(self.temperature)
                else:
                    print("Error: Temperature outside of valid range.")
                    raise ValueError()
            else:
                self.viscosity = float(self.viscosity)
            self.start_pos = self.phys.get('start_pos')
            self.start_pos = np.array(self.start_pos.split(','),
                                      dtype=float)
            if self.start_pos.shape != (3,):
                raise ValueError()
            if self.phys.get('shape') == 'Sphere':
                self.radius = self.phys.getfloat('radius_sphere')
                self.frictional_drag_linear = 6*pi*self.viscosity*self.radius
                self.frictional_drag_rotational\
                    = 8*pi*self.viscosity*(self.radius**3)
            elif self.phys.get('shape') == 'Ellipsoid':
                self.radius_major = self.phys.getfloat('radius_major')
                self.radius_minor = self.phys.getfloat('radius_minor')
                q = np.log(2*self.radius_major/self.radius_minor)
                self.frictional_drag_linear\
                    = 6*pi*self.viscosity*self.radius_major/q
                self.frictional_drag_rotational\
                    = (8*pi*self.viscosity*(self.radius_major**3)/3)/(q+0.5)
            else:
                print("Error: Shape not found")
                raise ValueError()
            self.diffusion_constant_linear\
                = self.temperature*boltz / self.frictional_drag_linear
            self.diffusion_constant_rotational\
                = self.temperature*boltz / self.frictional_drag_rotational
            self.sim_time = self.time.getfloat('sim_time')
            self.base_time = self.time.getfloat('base_time')
            self.sample_total = int(np.ceil(self.sim_time/self.base_time))
            self.sim_time = self.base_time*self.sample_total
            # Increases sim_time to include integer number of samples
            self.run_behaviour = self.bact.getboolean('run')
            self.run_duration_mean = self.bact.getfloat('run_mean')
            self.run_variation = self.bact.getboolean('run_var')
            self.run_length_mean\
                = int(np.round(self.run_duration_mean/self.base_time))
            self.run_speed = self.bact.getfloat('run_speed')
            self.run_step = self.run_speed*self.base_time
            self.archaea_mode = self.bact.getboolean('archaea_mode',
                                                     fallback=False)
            self.tumble_behaviour = self.bact.getboolean('tumble')
            self.tumble_duration_mean\
                = self.bact.getfloat('tumble_duration_mean')
            self.tumble_length_mean\
                = int(np.round(self.tumble_duration_mean
                               / self.base_time))
            self.tumble_duration_variation\
                = self.bact.getboolean('tumble_duration_var')
            self.tumble_type = self.bact.get('tumble_type')
            if self.tumble_type not in tumble_states:
                print("Error, %s is not a valid tumble mode." %
                      (self.tumble_type))
                raise ValueError()
            self.tumble_ang_vel = np.deg2rad(self.bact.getfloat(
                                                    'tumble_velocity'))
            self.tumble_ang_step = self.tumble_ang_vel*self.base_time
            self.chemotactic = self.chem.getboolean('chemotactic')
            self.chem_style = self.chem.get('chemotactic_style')
            if self.chem_style not in chem_styles:
                print("Error: %s not a valid chemotactic style"
                      % (self.chem_style))
                raise ValueError()
            self.chem_factor = self.chem.getfloat('chemotactic_factor')
            self.chem_memory = self.chem.getfloat('chemotactic_memory')
            self.chem_mem_size = int(self.chem_memory/self.base_time)
            self.chem_source = self.chem.get('chemotactic_source')
            self.chem_source = np.array(self.chem_source.split(','),
                                        dtype=float)
            if self.chem_source.shape != (3,):
                raise ValueError()
        except ValueError:
            print("Fatal Error: configuration %s is invalid.")
            sys.exit(1)
