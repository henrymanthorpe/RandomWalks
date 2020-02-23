#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 18:13:14 2020

@author: henry
"""

from Run import Bacteria
from Graphing import Graphing
import sys
import getopt
import os
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
    repeats = 1
    threads = 1
    try:
        opts, args = getopt.gnu_getopt(argv[1:], 'hc:r:t:',['help','repeats=','threads='])
    except getopt.GetoptError:
        print(help_text)
        sys.exit()
    for opt, var in opts:
        if opt in ('-h','--help'):
            print(help_text)
            sys.exit()
        elif opt in ('-r','--repeats'):
            repeats = int(var)
        elif opt in ('-t','--threads'):
            threads = int(var)
        else:
            assert False
    if len(args) == 0:
        args.append(os.getcwd())
    for arg in args:
        if not arg.endswith('/',-1):
            arg = arg+'/'
        print("Running in "+arg)
        if not os.path.exists(arg):
            print("Error: No such directory exists.")
            print(help_text)
            sys.exit()
        config_dir = arg+'configs/'
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
            print("Config Directory not found, making "+config_dir)
            Default()
            sys.exit()
        plot_dir = arg+'plots/'
        if not os.path.exists(plot_dir):
            os.mkdir(plot_dir)
            print("Plot Directory not found, making "+plot_dir)
        graph_dir = arg+'graphs/'
        if not os.path.exists(graph_dir):
            os.mkdir(graph_dir)
            print("Graph Directory not found, making "+graph_dir)

        bact = Bacteria()
        bact.ConfigSweep_Parallel(arg,repeats,threads)
        graph = Graphing(bact, graph_dir)
        graph.BrownianDiffusionConstants()
        graph.MotilityDiffusionConstants()

if __name__== '__main__':
    main(sys.argv)
            