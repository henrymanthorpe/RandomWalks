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
from Config import Default


def main(argv):
    parser = argparse.ArgumentParser(description='Run Bacterial Simulation')
    parser.add_argument('-t', '--threads', dest='threads', default=1,
                        type=int, help='Number of HW threads to use')
    parser.add_argument('-r', '--repeats', dest='repeats', default=1,
                        type=int, help='Number of repeats per config')
    parser.add_argument('-i', '--import', dest='importing',
                        action='store_true',
                        help='Import previous trajectories and rerun analysis')
    parser.add_argument('-d', '--default', dest='default',
                        action='store_true',
                        help='Save Default config file to CWD')
    parser.add_argument('-o', '--overwrite', dest='overwrite',
                        action='store_true',
                        help='Overwrite Mode: Clears previous results and'
                        + ' resimulates all values.')
    parser.add_argument('-a', '--append', dest='append', action='store_true',
                        help='Append Mode: Keeps previous results and'
                        + 'simulates new values up to <repeats>')
    parser.add_argument('-g', '--graph', dest='graph', action='store_true',
                        help='Run analysis routine')
    parser.add_argument('-vis', '--visualisation', dest='vis',
                        action='store_true',
                        help='Exports data in visualisation format')
    parser.add_argument('batches', nargs='*',
                        help='Root Directory for batch files')
    args = parser.parse_args()
    print(args)
    mode = None
    if args.default:
        Default()
        sys.exit()
    if len(args.batches) == 0:
        parser.parse_args(['-h'])
        sys.exit()
    if not args.importing:
        if args.append:
            mode = True
        elif args.overwrite:
            mode = False
        elif args.append and args.overwrite:
            print("Error: Cannot run in both Overwrite and Append modes")
            parser.parse_args(['-h'])
            sys.exit()
        elif not args.append and not args.overwrite:
            print("Error: No mode Specified (Overwrite/Append) ")
            parser.parse_args(['-h'])
            sys.exit()
    if args.importing:
        if not args.graph and not args.visualisation:
            print("Error: Importing data for no reason (graph/vis)")
            parser.parse_args(['-h'])
            sys.exit()
    for arg in args.batches:
        print("Running in "+arg)
        if not os.path.exists(arg):
            print("Error: No such directory exists. (%s) " % (arg))
            parser.parse_args(['-h'])
            sys.exit()
        config_dir = os.path.join(arg, 'configs')
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)
            print("Config Directory not found, making %s " % (config_dir))
        plot_dir = os.path.join(arg, 'plots')
        if not os.path.exists(plot_dir):
            os.mkdir(plot_dir)
            print("Plot Directory not found, making %s " % (plot_dir))
        graph_dir = os.path.join(arg, 'graphs')
        if not os.path.exists(graph_dir):
            os.mkdir(graph_dir)
            print("Graph Directory not found, making %s " % (graph_dir))
        traj_dir = os.path.join(arg, 'trajectories')
        if not os.path.exists(traj_dir):
            os.mkdir(traj_dir)
            print("Trajectory Directory not found, making %s " % (traj_dir))
        cosine_dir = os.path.join(arg, 'cosines')
        if not os.path.exists(cosine_dir):
            os.mkdir(cosine_dir)
            print("Cosines Directory not found, making %s " % (cosine_dir))

        if len(os.listdir(config_dir)) == 0:
            print("No config files found in %s" % (config_dir))
            Default(config_dir)
            sys.exit()
        start = time.time()
        batch = Bacteria()
        if args.importing:
            batch.Import(config_dir, traj_dir, cosine_dir)
            print('Import Complete for %s' % (arg))
        else:
            batch.ConfigSweep_Parallel(config_dir, traj_dir, cosine_dir,
                                       args.repeats, args.threads, mode)
            end = time.time()
            print('Simulation complete for %s' % (arg))
            print("Computation time = %f s" % (end-start))

        if args.graph:
            graph = Graphing(batch, graph_dir, plot_dir, args.threads)
            graph.DiffusionConstants()

        if args.vis:
            pass


if __name__ == '__main__':
    main(sys.argv)
