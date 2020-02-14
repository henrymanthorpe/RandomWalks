#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 22:35:50 2020

@author: henry
"""
import configparser
import numpy as np

def Input():
    
    config = configparser.ConfigParser(allow_no_value=True)
    print("Welcome to the guided Variable builder \n")
    print("--- Particle Variables ---")
    phys = {}
    while True:
        try:
            mol_mass = input("Input molecular mass of the particle (kg/mol) :")
            if float(mol_mass) > 0:
                phys['mol_mass'] = mol_mass
                break
            else:
                print("Error: Negative Mass not possible")
        except ValueError:
            print("Error: That is not a numerical input")
    while True:
        try:
            particle_shape = input("Select particle shape - (S)phere or (E)llipsoid (ELLIPSOIDS CURRENTLY DON'T WORK) : ")
            if particle_shape.upper() == 'E' or particle_shape.lower()=='ellipsoid':
                phys['shape'] = 'Ellipsoid'
                phys['radius_sphere'] = ''
                while True:
                    try:
                        radius_major = input("Input semi-major axis (m) : ")
                        if float(radius_major) > 0:
                            phys['radius_major'] = radius_major
                            break
                        else:
                            print("Error: Negative value not possible")
                    except ValueError:
                        print("Error: That is not a numerical input")
                while True:
                    try:
                        radius_minor = input("Input semi-minor axis (m) : ")
                        if float(radius_minor) > 0:
                            break
                        else:
                            print("Error: Negative value not possible")
                    except ValueError:
                        print("Error: That is not a numerical input")
                break

            elif particle_shape.upper() == 'S' or particle_shape.lower()=='sphere':
                phys['shape'] = 'Sphere'
                while True:
                    try:
                        radius_sphere = input("Input spherical radius (m) : ")
                        if float(radius_sphere) > 0:
                            phys['radius_sphere'] = radius_sphere
                            phys['radius_major'] = ''
                            phys['radius_minor'] = ''
                            break
                        else:
                            print("Error: Negative value not possible")
                    except ValueError:
                        print("Error: That is not a numerical input")
                break

            else:
                print("Error:Not a valid input")
        except SyntaxError:
            print("Error: That is not an allowed input (Syntax Error)")

    print("\n--System Variables--")
    env = {}
    while True:
        try:
            temp = input("Input absolute temperature (K) : ")
            if float(temp) > 0:
                env['temp'] = temp
                break
            else:
                print("Error: Negative value not possible")
        except ValueError:
            print("Error: That is not a numerical input")
    while True:
        try:
            viscosity = input("Input absolute viscosity kg/(m*s) : ")
            if float(viscosity) > 0:
                env['viscosity'] = viscosity
                break
            else:
                print("Error: Negative value not possible")
        except ValueError:
            print("Error: That is not a numerical input")

    while True:
        try:
            force_input = input("Input external forces (x,y,z) (N) : ")
            external_forces = np.asarray(force_input.split(','), dtype=float)
            if len(external_forces.shape) == 1 and external_forces.shape[0]==3:
                env['f_x'] = force_input[0]
                env['f_y'] = force_input[1]
                env['f_z'] = force_input[2]
                break
            else:
                print("Error: Requires three inputs")
        except ValueError:
            print("Error: That is not a numerical input")
    print("\n--Time Variables--")
    time = {}
    while True:
        try:
            run_time = input("Input run time (s) : ")
            if float(run_time) > 0:
                time['run_time'] = run_time
                break
            else:
                print("Error: Negative value not possible")
        except ValueError:
            print("Error: That is not a numerical input")
    while True:
        try:
            base_time = input("Input base time (s) : ")
            if float(base_time) > 0:
                env['base_time'] = base_time
                break
            else:
                print("Error: Negative value not possible")
        except ValueError:
            print("Error: That is not a numerical input")
    print("\n--Run&Tumble Variables--")
    bact = {}
    while True:
        try:
            run_behaviour = input("Run & Tumble Behaviour required? (Y)es or (N)o : ")
            if run_behaviour.lower() == 'yes' or run_behaviour.lower() == 'y':
                bact['run'] = 'yes'
                while True:
                    try:
                        run_speed = input("Input average run speed (m/s) : ")
                        if float(run_speed) > 0:
                            bact['run_speed'] = run_speed
                            break
                        else:
                            print("Error: Negative value not possible")
                    except ValueError:
                        print("Error: That is not a numerical input")
                while True:
                    try:
                        run_var = input("Is run duration (C)onstant or (D)istributed randomly? : ")
                        if run_var.lower() == 'c' or run_var.lower == 'constant':
                            bact['run_var'] = 'no'
                            break
                        elif run_var.lower() == 'd' or run_var.lower == 'distributed':
                            bact['run_var'] = 'yes'
                            break
                        else:
                            print("Error: Not a valid input.")
                    except SyntaxError:
                        print("Error: That is not an allowed input (Syntax Error).")
                while True:
                    try:
                        run_mean = input("Input average run duration (s) : ")
                        if float(run_mean) > 0:
                            bact['run_mean'] = run_mean
                            break
                        else:
                            print("Error: Negative value not possible")
                    except ValueError:
                        print("Error: That is not a numerical input")
                while True:
                    try:
                        tumble_behaviour = input("Tumble Behaviour - (A)ctive or (P)assive? : ")
                        if tumble_behaviour.lower() == 'a' or tumble_behaviour.lower() == 'active':
                            bact['tumble'] = 'yes'
                            while True:
                                try:
                                    tumble_angle_var = input("Is tumble angle (C)onstant or (D)istributed randomly? : ")
                                    if tumble_angle_var.lower() == 'c' or tumble_angle_var.lower == 'constant':
                                        bact['tumble_angle_var'] = 'no'
                                        break
                                    elif tumble_angle_var.lower() == 'd' or tumble_angle_var.lower == 'distributed':
                                        bact['tumble_angle_var'] = 'yes'
                                        break
                                    else:
                                        print("Error: Not a valid input.")
                                except SyntaxError:
                                    print("Error: That is not an allowed input (Syntax Error).")
                            while True:
                                try:
                                    tumble_angle_mean = input("Input average tumble angle (degrees) : ")
                                    if float(tumble_angle_mean) >= 0 and float(tumble_angle_mean) <= 360:
                                        bact['tumble_angle_mean'] = tumble_angle_mean
                                        break
                                    else:
                                        print("Error: Please input value between 0 and 360 inclusive")
                                except ValueError:
                                    print("Error: That is not a numerical input")
                            while True:
                                try:
                                    tumble_duration_var = input("Is tumble duration (C)onstant or (D)istributed randomly? : ")
                                    if tumble_duration_var.lower() == 'c' or tumble_duration_var.lower == 'constant':
                                        bact['tumble_duration_var'] = 'no'
                                        break
                                    elif tumble_duration_var.lower() == 'd' or tumble_duration_var.lower == 'distributed':
                                        bact['tumble_duration_var'] = 'yes'
                                        break
                                    else:
                                        print("Error: Not a valid input.")
                                except SyntaxError:
                                    print("Error: That is not an allowed input (Syntax Error).")
                            while True:
                                try:
                                    tumble_duration_mean = input("Input average tumble duration (s) : ")
                                    if float(tumble_duration_mean) > 0:
                                        bact['tumble_duration_mean'] = tumble_duration_mean
                                        break
                                    else:
                                        print("Error: Negative value not possible")
                                except ValueError:
                                    print("Error: That is not a numerical input")
                            bact['pause_var'] = ''
                            bact['pause_mean'] = ''
                            break
                        elif tumble_behaviour.lower() == 'p' or tumble_behaviour.lower() == 'passive':
                            bact['tumble'] = 'no'
                            bact['tumble_angle_var'] = ''
                            bact['tumble_angle_mean'] = ''
                            bact['tumble_duration_var'] = ''
                            bact['tumble_duration_mean'] = ''
                            while True:
                                try:
                                    pause_var = input("Is tumble duration (C)onstant or (D)istributed randomly? : ")
                                    if pause_var.lower() == 'c' or pause_var.lower == 'constant':
                                        bact['pause_var'] = 'no'
                                    elif pause_var.lower() == 'd' or pause_var.lower == 'distributed':
                                        bact['pause_var'] = 'yes'
                                        break
                                    else:
                                        print("Error: Not a valid input.")
                                except SyntaxError:
                                    print("Error: That is not an allowed input (Syntax Error).")
                            while True:
                                try:
                                    pause_mean = input("Input average tumble duration (s) : ")
                                    if float(pause_mean) >= 0:
                                        bact['tumble_duration_mean'] = pause_mean
                                        break
                                    else:
                                        print("Error: Negative value not possible")
                                except ValueError:
                                    print("Error: That is not a numerical input")
                            break
                        else:
                            print('Error: Not a valid input.')
                    except SyntaxError:
                        print("Error: That is not an allowed input (Syntax Error)")
                    break
                break
            elif run_behaviour.lower() == 'no' or run_behaviour.lower() == 'n':
                bact['run'] = 'no'
                bact['run_speed'] = ''
                bact['run_var'] = ''
                bact['run_mean'] = ''
                bact['tumble'] = ''
                bact['tumble_angle_var'] = ''
                bact['tumble_angle_mean'] = ''
                bact['tumble_duration_var'] = ''
                bact['tumble_duration_mean'] = ''
                bact['pause_var'] = ''
                bact['pause_mean'] = ''
                break
            else:
                print('Error: Not a valid input.')
        except SyntaxError:
            print("Error: That is not an allowed input (Syntax Error)")
            
    config_dict = {'phys':phys,'env':env,'time':time,'bact':bact}
    config.read_dict(config_dict)
    with open('interactive.in','w') as interactive_save:
        config.write(interactive_save)
    print("\nConfig saved to interactive.in for future use/reference")
    print("Exiting guided Variable builder")
    return config

    
            
                            
                            