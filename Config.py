#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 19:48:13 2020

@author: henry
"""
import os
import configparser


def Default(save_dir='', verb=True):
    default_config = """
# Simulation Configuration File

# DO NOT use an underscore in the file name, it will break importing later.

[name]

# Name - Configuration descriptor, used to identify in Analysis graphs
# If left blank, configuration file name will be used.

name =

[phys]
# Bacteria Physical Variables

# Bacteria shape (Sphere or Ellipsoid)
shape = Sphere

# Spherical radius (if Sphere)  (metres)
radius_sphere = 0.5e-6

# Semi-Major and Semi-Minor axis radii (if Ellipsoid) (metres)
radius_major =
radius_minor =

# Start Position (m)
start_pos = 0,0,0

[env]
# Environment Variables

# Defaults are for water in Standard Conditions

# System Temperature (K)
temp = 297.0

# Absolute Viscosity of the medium (Pa*s)
# 'water' provides semi-empirical value for viscosity
# at one atmosphere for 273 <= T <= 373
viscosity = 8.9e-4

[time]
# Simulation Variables

# Total simulation time (s)
sim_time = 600.0

# Interval (step) time (s)
base_time = 5e-3

# For these values, Computation time per repeat ~ 1 minute
# and produces ~ 11MB of trajectory data per repeat

[bact]
# Diffusion Behaviour - Turn off to remove all Brownian motion effects

diffusive = yes

# Run-Tumble Variables

# Run Behaviour
run = yes

# Run Speed (N)
run_force = 1.25e-13

# Varying Run Duration
run_var = yes

# Mean Run Duration (s)
run_mean = 0.9

#Tumble Behaviour
tumble = yes

#Tumble type - smooth, erratic, pause
tumble_type = erratic

#Tumble Duration Variation
tumble_duration_var = yes

#Mean Tumble Duration (s)
tumble_duration_mean = 0.1

# Tumble Torque (Nm)
tumble_torque = 2e-19


# Archaea mode - Run and Reverse
archaea_mode = no

[chem]
# Chemotactic Variables

# Chemotactic Behaviour
chemotactic = no

# Chemotactic Style (linear)
chemotactic_style = linear

# Chemotactic Axis/Source
chemotactic_source = 0,0,1

# Chemotactic Factor
chemotactic_factor = 1

# Chemotactic Memory (s)
chemotactic_memory = 0.1

[seed]
#RNG Variables

# If a fixed seed is wanted to get repeatability,
# provide an entropy integer here
# Else, leave blank for normal use.
entropy =

    """
    if save_dir == '':
        save_dir = 'Current Working Directory'
        fname = 'defaultconfig.in'
    else:
        fname = os.path.join(save_dir, 'defaultconfig.in')
    f = open(fname, 'w')
    f.write(default_config)
    f.close()
    if verb:
        print("Default Config File created as 'defaultconfig.in' in %s"
              % (save_dir))
        print("Please edit the contained values "
              + "to those required for your needs.")


def GetConfig(fname):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(fname)
    return config
