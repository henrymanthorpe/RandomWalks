#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 19:48:13 2020

@author: henry
"""
import os
import configparser


def Default(save_dir=''):
    default_config = """
# Default Configuration File

[phys]
# Bacteria Physical Variables

# Molecular mass of bacteria strain (kg/mol)
mol_mass = 15

# Bacteria shape (Sphere or Ellipsoid)
shape = Sphere

# Spherical radius (if Sphere)
radius_sphere = 1e-6

# Semi-Major and Semi-Minor axis radii (if Ellipsoid)
radius_major =
radius_minor =

# Start Position (m)
start_pos = 0,0,0

[env]
# Environment Variables

# Defaults are for water in Standard Conditions

# System Temperature (K)
temp = 297

# Absolute Viscosity of the medium (kg/(m*s))
viscosity = 8.9e-4

[time]
# Simulation Variables

# Total simulation time (s)
sim_time = 600

# Interval (step) time (s)
base_time = 10e-3

[bact]
# Run-Tumble Variables

# Run Behaviour
run = yes

# Run Speed (m/s)
run_speed = 1.5e-5

# Varying Run Duration
run_var = yes

# Mean Run Duration (s)
run_mean = 0.9

#Tumble Behaviour
tumble = yes

#Tumble type - smooth, erratic, pause
tumble_type = smooth

#Tumble Duration Variation
tumble_duration_var =yes

#Mean Tumble Duration (s)
tumble_duration_mean = 0.1

# Mean Tumble Angular Velocity (degrees/sec)
tumble_velocity = 650


# Archaea mode - Run and Reverse
archaea_mode = no

[chem]
# Chemotactic Variables

# Chemotactic Behaviour
chemotactic = no

# Chemotactic Style (linear/point)
chemotactic_style = linear

# Chemotactic Axis/Source
chemotactic_source = 0,0,1

# Chemotactic Factor
chemotactic_factor = 2

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
    print("Default Config File created as 'defaultconfig.in' in %s"
          % (save_dir))
    print("Please edit the contained values to those required for your needs.")


def GetConfig(fname):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(fname)
    return config
