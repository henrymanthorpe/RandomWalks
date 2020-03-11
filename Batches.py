#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 22:55:08 2020

@author: henry
"""
import sys
import os
import configparser
import numpy as np
from Config import GetConfig, Default
from tempfile import TemporaryDirectory


def MakeBatch():
    print('Enter Batch Directory Name for new batch.')
    batch_dir = input('>> ')
    print('Enter Batch prefix.')
    print('Warning, all configuration files with the same prefix will'
          +' be deleted and replaced with new ones upon export.')
    batch_name = input('>> ')
    config_dir = os.path.join(batch_dir, 'configs')
    if not os.path.exists(batch_dir):
        os.mkdir(batch_dir)
        os.mkdir(config_dir)
    elif not os.path.exists(config_dir):
        os.mkdir(config_dir)
    while True:
        try:
            print('Enter total number of configurations.')
            total_configs = int(input('>> '))
            print("Total configs =  %d" % (total_configs))
            break
        except ValueError:
            print("Error: input is not a valid number.")
            continue
    temp = TemporaryDirectory()
    while True:
        print("Enter filename of the base configuration,")
        print('or enter "default" to use the default configuration.')
        config_input = input('>> ')
        if config_input == 'default':
            Default(temp.name, False)
            config_input = os.path.join(temp.name, 'defaultconfig.in')
            break
        elif os.path.exists(config_input):
            break
        else:
            print('Error: File does not exist:')
            continue
    initial_config = GetConfig(config_input)
    batch_config = [GetConfig(config_input) for i in range(total_configs)]
    temp.cleanup()
    cancel = False
    while True:
        print('Enter Section and key name, (seperated by whitespace)')
        print('Enter "export" to write batch configuration files,')
        print('Or enter "cancel" to quit without saving')
        user_input = input('>> ')
        if user_input == 'cancel':
            cancel = True
            break
        elif user_input == 'export':
            break
        elif len(user_input.split()) == 2:
            section, key = user_input.split()
            print('Input Successful')
        else:
            print('Error: Input of %s is invalid.' % (user_input))
            continue
        if section in initial_config.sections():
            if key in initial_config[section].keys():
                print("Key: %s, \t Current Value: %s" % (key,
                                                         initial_config
                                                         [section][key]))
            else:
                print('%s is not a valid key.')
                break
        else:
            print('%s is not a valid section')
            break
        while True:
            print('Enter scale choice. (linear/logarithimic/manual)')
            user_input = input('>> ')
            if user_input.startswith('lin'):
                print("Linear scale selected.")
                scale = 'linear'
                break
            elif user_input.startswith('log'):
                print("Logarithmic scale selected.")
                scale = 'logarithmic'
                break
            elif user_input.startswith('man'):
                print('Manual scale selected')
                scale = 'manual'
                break
            else:
                print("Error: input of %s is invalid" % (user_input))
                continue
        if scale == 'linear':
            while True:
                try:
                    print('Enter initial and final values. '
                          + '(seperated by whitespace) ')
                    print('Initial < Final')
                    start, stop = input('>> ').split()
                    start = float(start)
                    stop = float(stop)
                    if stop-start <= 0:
                        raise ValueError()
                    steps = np.linspace(start, stop, total_configs)
                    break
                except ValueError:
                    print('Error: Input is invalid')
                    continue
        elif scale == 'logarithmic':
            while True:
                try:
                    print("Scale = multiplier x base^(exponent) ")
                    print('Enter multiplier value.')
                    factor = input('>>')
                    print('Enter base value.')
                    base = input('>> ')
                    print('Enter initial and final exponents. '
                          + '(seperated by whitespace) ')
                    print('Initial < Final')
                    start, stop = input('>> ').split()
                    factor = float(factor)
                    base = float(base)
                    start = float(start)
                    stop = float(stop)
                    if stop-start <= 0:
                        raise ValueError()
                    steps = factor *\
                        np.logspace(start, stop, total_configs, base=base)
                    break
                except ValueError:
                    print('Error: Input is invalid')
                    continue
        elif scale == 'manual':
            while True:
                print('Enter %d values (seperated by whitespace)' %
                      (total_configs))
                user_input = input(">> ")
                steps = user_input.split()
                if len(steps) == total_configs:
                    break
                elif len(steps) < total_configs:
                    print('Error: User entered insufficient values')
                elif len(steps) > total_configs:
                    print('Error: User entered too many values')
        if scale == 'manual':
            for i in range(total_configs):
                batch_config[i][section][key] = '%s' % (steps[i])

        else:
            for i in range(total_configs):
                batch_config[i][section][key] = '%8.3g' % (steps[i])
        print("Values:")
        print(steps)
        continue

    if not cancel:
        for entry in os.scandir(batch_dir):
            if os.path.split(entry.path)[1].startswith(batch_name):
                os.remove(entry.path)
        digits = int(np.ceil(np.log10(total_configs+1)))
        for i in range(total_configs):
            file_iter = str(i)
            while len(file_iter) < digits:
                file_iter = '0'+file_iter
            fname = "%s%s.in" % (batch_name, file_iter)
            save_name = os.path.join(config_dir, fname)
            with open(save_name, 'w') as f:
                batch_config[i].write(f)
                f.close()
        print("Written %d configurations to %s" % (total_configs, config_dir))
        return batch_dir
    else:
        print("Batch aborted by user.")
        return ''


def BatchBuilder():
    print("Welcome to the Batch Builder")
    print("----------------------------")
    batches = []
    while True:
        new_batch = MakeBatch()
        if new_batch not in batches and new_batch != '':
            batches.append(new_batch)
        while True:
            print("Make another batch? (y/n)")
            user_input = input('>> ')
            if user_input.lower() in ['y', 'yes']:
                break
            elif user_input.lower() in ['n', 'no']:
                return batches
            else:
                print("Error: input not valid.")
                continue
