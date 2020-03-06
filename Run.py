#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 10:56:16 2020

@author: henry
"""

from Simulate import Bacterium
from Input import Variables
import os
import time
import numpy as np

try:
    from joblib import Parallel, delayed
except ImportError:
    print('joblib not found, parallelisation not available')


def SingleRun(fname, bact, traj_dir):
    print("Started\t Config: %s \t %s \t" % (os.path.split(fname)[0], bact))
    start = time.time()
    bacterium = Bacterium(fname)
    bacterium.Complete()
    save_tup = (bacterium.time, bacterium.displacement,
                bacterium.total_displacement, bacterium.vectors_cartesian)
    export = np.hstack(save_tup)
    txt_name = os.path.join(traj_dir, "%s_%s.txt" % (
        os.path.splitext(os.path.split(fname)[1])[0], bact))
    np.savetxt(txt_name, export)
    end = time.time()
    elapsed = end-start
    print("Finished\t Config: %s \t %s \tTime taken %d" % (
        os.path.split(fname)[0], bact, elapsed))
    return txt_name



class Bacteria:

    def __init__(self):
        self.config = {}
        self.bacterium = {}

    def ConfigSweep(self, config_dir, repeats):
        self.schedule_array = []
        for entry in os.scandir(config_dir):
            if entry.path.endswith('.in', -3):
                self.config[os.path.splitext(os.path.split(entry.path)
                                             [-1])[0]] = entry.path
                self.bacterium[os.path.splitext(os.path.split(entry.path)
                                                [-1])[0]] = {}
                for i in range(repeats):
                    self.schedule_array.append(['', '', ''])
                    self.schedule_array[-1][0] = os.path.splitext(
                        os.path.split(entry.path)[-1])[0]
                    self.schedule_array[-1][1] = 'bact'+str(i)
                    self.schedule_array[-1][2] = entry.path
        out = [SingleRun(self.schedule_array[i][2])
               for i in range(len(self.schedule_array))]
        for i in range(len(self.schedule_array)):
            self.bacterium[self.schedule_array[i][0]][
                self.schedule_array[i][1]] = out[i]

    def ConfigSweep_Parallel(self, config_dir, traj_dir, repeats, threads):
        with Parallel(n_jobs=threads) as parallel:
            self.schedule_array = []
            for entry in os.scandir(config_dir):
                if entry.path.endswith('.in', -3):
                    self.config[os.path.splitext(os.path.split(entry.path)
                                                 [-1])[0]]\
                        = Variables(entry.path)
                    self.bacterium[os.path.splitext(os.path.split(entry.path)
                                                    [-1])[0]] = {}
                    for i in range(repeats):
                        self.schedule_array.append(['', '', ''])
                        self.schedule_array[-1][0] = os.path.splitext(
                            os.path.split(entry.path)[-1])[0]
                        self.schedule_array[-1][1] = 'bact'+str(i)
                        self.schedule_array[-1][2] = entry.path
            out = parallel(delayed(SingleRun)(self.schedule_array[i][2],
                                              self.schedule_array[i][1],
                                              traj_dir)
                           for i in range(len(self.schedule_array)))
            for i in range(len(self.schedule_array)):
                self.bacterium[self.schedule_array[i][0]][
                    self.schedule_array[i][1]] = out[i]
