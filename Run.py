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


def SingleRun(fname, bact, traj_dir, cosine_dir, append):
    print("Started\t Config: %s \t %s \t" % (os.path.split(fname)[0], bact))
    traj_save_dir = os.path.join(traj_dir,
                                 os.path.splitext(os.path.split(fname)[1])[0])
    cosine_save_dir = os.path.join(cosine_dir,
                                   os.path.splitext(
                                       os.path.split(fname)[1])[0])
    if not os.path.exists(traj_save_dir):
        os.mkdir(traj_save_dir)
    if not os.path.exists(cosine_save_dir):
        os.mkdir(cosine_save_dir)
    traj_name = os.path.join(traj_save_dir, bact+".txt")
    cosine_name = os.path.join(cosine_save_dir, bact+'.txt')
    if os.path.exists(traj_name) and os.path.exists(cosine_name) and append:
        print("Value prexists, not recalulating")
        return [traj_name, cosine_name]
    start = time.time()
    bacterium = Bacterium(fname)
    bacterium.Complete()
    save_tup = (bacterium.time, bacterium.displacement,
                bacterium.vectors_cartesian)
    export = np.hstack(save_tup)
    np.savetxt(traj_name, export, fmt='%+.5e', delimiter='\t')
    cosine_array = bacterium.run_run_cosines
    np.savetxt(cosine_name, cosine_array, fmt='%+.8e', delimiter='\t')
    end = time.time()
    elapsed = end-start
    print("Finished\t Config: %s \t %s \tTime taken %d" % (
        os.path.split(fname)[0], bact, elapsed))
    return [traj_name, cosine_name]


class Bacteria:

    def __init__(self):
        self.config = {}
        self.bacterium = {}
        self.cosines = {}

    # def ConfigSweep(self, config_dir, repeats):
    #     self.schedule_array = []
    #     for entry in os.scandir(config_dir):
    #         if entry.path.endswith('.in', -3):
    #             self.config[os.path.splitext(os.path.split(entry.path)
    #                                          [-1])[0]] = entry.path
    #             self.bacterium[os.path.splitext(os.path.split(entry.path)
    #                                             [-1])[0]] = {}
    #             for i in range(repeats):
    #                 self.schedule_array.append(['', '', ''])
    #                 self.schedule_array[-1][0] = os.path.splitext(
    #                     os.path.split(entry.path)[-1])[0]
    #                 self.schedule_array[-1][1] = 'bact'+str(i)
    #                 self.schedule_array[-1][2] = entry.path
    #     out = [SingleRun(self.schedule_array[i][2])
    #            for i in range(len(self.schedule_array))]
    #     for i in range(len(self.schedule_array)):
    #         self.bacterium[self.schedule_array[i][0]][
    #             self.schedule_array[i][1]] = out[i]

    def Import(self, config_dir, traj_dir, cosine_dir):
        for entry in os.scandir(config_dir):
            if entry.path.endswith('.in', -3):
                self.config[os.path.splitext(os.path.split(entry.path)
                                             [-1])[0]] = Variables(entry.path)
                self.bacterium[os.path.splitext(os.path.split(entry.path)
                                                [-1])[0]] = {}
                self.cosines[os.path.splitext(os.path.split(entry.path)
                                              [-1])[0]] = {}
        for entry in os.scandir(traj_dir):
            if entry.is_dir():
                for traj_file in os.scandir(entry):
                    self.bacterium[os.path.split(entry)[-1]]\
                        [os.path.split(os.path.splitext(traj_file)[0])[-1]]\
                        = traj_file.path
        for entry in os.scandir(cosine_dir):
            if entry.is_dir():
                for cosine_file in os.scandir(entry):
                    self.cosines[os.path.split(entry)[-1]]\
                        [os.path.split(os.path.splitext(cosine_file)[0])[-1]]\
                        = cosine_file.path

    def ConfigSweep_Parallel(self, config_dir, traj_dir, cosine_dir,
                             repeats, threads, append):
        with Parallel(n_jobs=threads) as parallel:
            self.schedule_array = []
            if not append:
                for entry in os.scandir(traj_dir):
                    if entry.is_dir():
                        for traj_file in os.scandir(entry):
                            os.remove(traj_file)
                    os.rmdir(entry)
                for entry in os.scandir(cosine_dir):
                    if entry.is_dir():
                        for cosine_file in os.scandir(entry):
                            os.remove(cosine_file)
                    os.rmdir(entry)
            for entry in os.scandir(config_dir):
                if entry.path.endswith('.in', -3):
                    self.config[os.path.splitext(os.path.split(entry.path)
                                                 [-1])[0]]\
                        = Variables(entry.path)
                    self.bacterium[os.path.splitext(os.path.split(entry.path)
                                                    [-1])[0]] = {}
                    self.cosines[os.path.splitext(os.path.split(entry.path)
                                                  [-1])[0]] = {}
                    for i in range(repeats):
                        self.schedule_array.append(['', '', ''])
                        self.schedule_array[-1][0] = os.path.splitext(
                            os.path.split(entry.path)[-1])[0]
                        self.schedule_array[-1][1] = 'bact'+str(i)
                        self.schedule_array[-1][2] = entry.path
            out = parallel(delayed(SingleRun)(self.schedule_array[i][2],
                                              self.schedule_array[i][1],
                                              traj_dir, cosine_dir, append)
                           for i in range(len(self.schedule_array)))
            for i in range(len(self.schedule_array)):
                self.bacterium[self.schedule_array[i][0]][
                    self.schedule_array[i][1]] = out[i][0]
                self.cosines[self.schedule_array[i][0]][
                    self.schedule_array[i][1]] = out[i][1]
