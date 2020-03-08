#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 22:04:35 2020

@author: henry
"""
import Config
import Interactive
import numpy as np
from scipy import constants
import sys


class Variables:

    def __init__(self, fname=""):
        tumble_states = ['smooth', 'erratic', 'pause']
        chem_styles = ['linear', 'point']
        pi = np.pi
        boltz = constants.Boltzmann
        avo = constants.Avogadro
        try:

            config = Config.GetConfig(fname)
            if config.sections() == ['phys', 'env', 'time', 'bact',
                                     'chem', 'seed']:
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
            self.particle_mass = self.phys.getfloat('mol_mass')/avo
            self.viscosity = self.env.getfloat('viscosity')
            self.temperature = self.env.getfloat('temp')
            if self.phys.get('shape') == 'Sphere':
                self.radius = self.phys.getfloat('radius_sphere')
                self.frictional_drag_linear = 6*pi*self.viscosity*self.radius
                self.frictional_drag_rotational\
                    = 8*pi*self.viscosity*(self.radius**3)
                self.MoI = 0.4*self.particle_mass*self.radius**2
            elif self.phys.get('shape') == 'Ellipsoid':
                self.radius_major = self.phys.getfloat('radius_major')
                self.radius_minor = self.phys.getfloat('radius_minor')
                q = np.log(2*self.radius_major/self.radius_minor)
                self.frictional_drag_linear\
                    = 6*pi*self.viscosity*self.radius_major/q
                self.frictional_drag_rotational\
                    = (8*pi*self.viscosity*(self.radius_major**3)/3)/(q+0.5)
                self.MoI = 0.2*self.particle_mass*(self.radius_major**2
                                                   + self.radius_minor**2)
            else:
                print("Error: Shape not found")
                raise ValueError()
            self.diffusion_constant_linear\
                = self.temperature*boltz / self.frictional_drag_linear
            self.diffusion_constant_rotational\
                = self.temperature*boltz / self.frictional_drag_rotational
            self.rms_velocity_linear\
                = np.sqrt(boltz*self.temperature/self.particle_mass)
            self.rms_velocity_rotational = np.sqrt(boltz*self.temperature
                                                   / self.MoI)
            self.step_linear\
                = 2*self.diffusion_constant_linear/self.rms_velocity_linear
            self.step_rate_linear = self.rms_velocity_linear/self.step_linear
            self.step_time_linear = 1.0/self.step_rate_linear
            self.sim_time = self.time.getfloat('sim_time')
            self.base_time = self.time.getfloat('base_time')
            self.sample_total = int(np.ceil(self.sim_time/self.base_time))
            self.sim_time = self.base_time*self.sample_total
            # Increases sim_time to include integer number of samples
            self.sample_steps_linear = self.step_rate_linear*self.base_time
            self.step_rotational\
                = 2*self.diffusion_constant_rotational\
                / self.rms_velocity_rotational
            self.step_rate_rotational\
                = self.rms_velocity_rotational/self.step_rotational
            self.step_time_rotational = 1.0/self.step_rate_rotational
            self.sample_steps_rotational = self.step_rate_rotational\
                * self.base_time
            self.run_behaviour = self.bact.getboolean('run')
            if self.run_behaviour is True:
                self.run_duration_mean = self.bact.getfloat('run_mean')
                self.run_variation = self.bact.getboolean('run_var')
                self.run_length_mean\
                    = int(np.round(self.run_duration_mean/self.base_time))
                self.run_speed = self.bact.getfloat('run_speed')
                self.run_step = self.run_speed*self.base_time
                self.archaea_mode = self.bact.getboolean('archaea_mode')
                self.tumble_behaviour = self.bact.getboolean('tumble')
                if self.tumble_behaviour is True:
                    self.tumble_duration_mean\
                        = self.bact.getfloat('tumble_duration_mean')
                    self.tumble_length_mean\
                        = int(np.round(self.tumble_duration_mean
                                       / self.base_time))
                    self.tumble_duration_variation\
                        = self.bact.getboolean('tumble_duration_var')
                    self.tumble_type = self.bact.get('tumble_type')
                    if self.tumble_type not in tumble_states:
                        raise ValueError()
                    self.tumble_ang_vel = np.deg2rad(self.bact.getfloat(
                                                            'tumble_velocity'))
                    self.tumble_ang_step = self.tumble_ang_vel*self.base_time
                else:
                    self.pause_variation = self.bact.getboolean('pause_var')
                    self.pause_duration_mean = self.bact.getfloat('pause_mean')
                    self.pause_length_mean\
                        = int(np.round(self.pause_duration_mean
                                       / self.base_time))
            self.chemotactic = self.chem.getboolean('chemotactic')
            self.chem_style = self.chem.get('chemotactic_style')
            if self.chem_style not in chem_styles:
                raise ValueError()
            self.chem_factor = self.chem.getfloat('chemotactic_factor')
            self.chem_memory = self.chem.getfloat('chemotactic_memory')
            self.chem_mem_size = int(self.chem_memory/self.base_time)
            self.chem_source = self.chem.get('chemotactic_source')
            self.chem_source = np.array(self.chem_source.split(','),
                                        dtype=float)
        except ValueError:
            sys.exit(1)
