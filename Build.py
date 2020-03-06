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
import numpy as np
from Config import Default

help_text = """ Build.py <directory> <-h/r/t --help/repeats/threads>
Runs all configs in directory for given number of repeats in parallel.
<directory> can either be given local to current working directory, or in
absolute form.
If left empty, runs in current working directory.
Multiple directories can be given, seperated by spaces

Imports
<directory>/configs/ -> contains config files to use (*.in format)

Exports
<directory>/plots/ -> Saved .dat files for gnuplot renders
<directory>/graphs/ -> Saved .emf graph output

--- Options ---
-h --help -> Shows this message
-r --repeats -> Number of repeats per config file (Default=1)
-t --threads -> Number of CPU threads to use for task (Default=1)

"""


def main(argv):
    parser = argparse.ArgumentParser(description='Run Bacterial Simulation')
    parser.add_argument('-t', '--threads', dest='threads', default=1,
                        type=int, help='Number of HW threads to use')
    parser.add_argument('-r', '--repeats', dest='repeats', default=1,
                        type=int, help='Number of repeats per config')
    parser.add_argument('-e', '--export', dest='export', action='store_true',
                        help='Export trajectories to file')
    parser.add_argument('-i', '--import', dest='import', action='store_true',
                        help='Import previous trajectories and rerun analysis')
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
        if not os.path.exists(traj_dir) and args.export is True:
            os.mkdir(traj_dir)
            print("Trajectory Directory not found, making "+traj_dir)

        if len(os.listdir(config_dir)) == 0:
            Default(config_dir)
            sys.exit()

        batch = Bacteria()
        batch.ConfigSweep_Parallel(config_dir, args.repeats, args.threads)
        if args.export is True:
            for key in batch.bacterium.keys():
                for bact in batch.bacterium[key].keys():
                    fname = key + '_' + bact + "_path.txt"
                    export = os.path.join(traj_dir, fname)
                    np.savetxt(export,
                               batch.bacterium[key][bact].displacement)
                    fname = key + '_' + bact + "_heading.txt"
                    export = os.path.join(traj_dir, fname)
                    np.savetxt(export,
                               batch.bacterium[key][bact].vectors_cartesian)
        graph = Graphing(batch, graph_dir, plot_dir)
        graph.MotilityDiffusionConstants()


if __name__ == '__main__':
    main(sys.argv)
