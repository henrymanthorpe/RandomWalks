#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 18:13:14 2020

@author: henry
"""

from Run import Bacteria
from Graphing import Graphing
import sys
import argparse
import os
import time
import numpy as np
from Config import Default


def main(argv):
    parser = argparse.ArgumentParser(description='Run Bacterial Simulation')
    parser.add_argument('-t', '--threads', dest='threads', default=1,
                        type=int, help='Number of HW threads to use')
    parser.add_argument('-r', '--repeats', dest='repeats', default=1,
                        type=int, help='Number of repeats per config')
    parser.add_argument('-i', '--import', dest='import', action='store_true',
                        help='Import previous trajectories and rerun analysis')
    parser.add_argument('-a', '--append', dest='append', action='store_true',
                        help='If True, writes additional values up to'
                        + ' repeat value, \n If False, clears values and'
                        + ' recaluates up to repeat value \n'
                        + 'Only use append if config file is unchanged')
    parser.add_argument('batches', nargs='*',
                        help='Root Directory for batch files')
    args = parser.parse_args()
    print(args)
    if len(args.batches) == 0:
        args.batches.append(os.path.relpath(os.getcwd()))
    for arg in args.batches:
        print("Running in "+arg)
        if not os.path.exists(arg):
            print("Error: No such directory exists.")
            parser.parse_args(['-h'])
            sys.exit()
        config_dir = os.path.join(arg, 'configs')
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
            print("Config Directory not found, making "+config_dir)
        plot_dir = os.path.join(arg, 'plots')
        if not os.path.exists(plot_dir):
            os.mkdir(plot_dir)
            print("Plot Directory not found, making "+plot_dir)
        graph_dir = os.path.join(arg, 'graphs')
        if not os.path.exists(graph_dir):
            os.mkdir(graph_dir)
            print("Graph Directory not found, making "+graph_dir)
        traj_dir = os.path.join(arg, 'trajectories')
        if not os.path.exists(traj_dir):
            os.mkdir(traj_dir)
            print("Trajectory Directory not found, making "+traj_dir)

        if len(os.listdir(config_dir)) == 0:
            Default(config_dir)
            sys.exit()
        start = time.time()
        batch = Bacteria()
        batch.ConfigSweep_Parallel(config_dir, traj_dir,
                                   args.repeats, args.threads, args.append)
        end = time.time()
        print("Computation time for "+arg+" = "+str(end-start)+" s")


if __name__ == '__main__':
    main(sys.argv)
