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
mol_mass = 10

# Bacteria shape (Sphere or Ellipsoid)
shape = Sphere

# Spherical radius (if Sphere)
radius_sphere = 1e-6

# Semi-Major and Semi-Minor axis radii (if Ellipsoid)
radius_major =
radius_minor =

[env]
# Environment Variables

# System Temperature (K)
temp = 297

# Absolute Viscosity of the medium (kg/(m*s))
viscosity = 8.9e-4

# Externally applied Force (N)
f_x = 0
f_y = 0
f_z = 0

# Modeling Gravitational acceleration?
gravity = no

[time]
# Simulation Variables

# Total simulation time (s)
sim_time = 20

# Interval (step) time (s)
base_time = 1e-3

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

# Varying Tumble Angle
tumble_angle_var = yes

# Mean Tumble angle (degrees)
tumble_angle_mean = 70

# Varying Tumble duration
tumble_duration_var = yes

# Mean Tumble duration (s)
tumble_duration_mean = 0.1

#(For No Tumbles - Rotation only by Diffusion)
# Varying Pause Duration
pause_var =

# Mean Pause Duration
pause_mean =

[chem]
# Chemotactic Variables

# Chemotactic Behaviour
chemotactic = no

# Chemotactic Style (linear/point)
chemotactic_style =

# Chemotactic Source (vector)
chemotactic_source =

[seed]
#RNG Variables

# If a fixed seed is wanted to get repeatability,
# provide an entropy integer here
# Else, leave blank for normal use.
entropy =

    """
    fname = os.path.join(save_dir, 'default_config.in')
    f = open(fname, 'w')
    f.write(default_config)
    f.close()
    print("Default Config File created as 'default_config.in' in "
          + save_dir + " \n")
    print("Please edit the contained values to those required for your needs.")


def GetConfig(fname):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(fname)
    return config
