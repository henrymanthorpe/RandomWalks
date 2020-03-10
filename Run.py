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


def SingleRun(fname, bact, traj_dir, cosine_dir, duration_dir, append):
    print("Started\t Config: %s \t %s \t" % (os.path.split(fname)[1], bact))
    traj_save_dir = os.path.join(traj_dir,
                                 os.path.splitext(os.path.split(fname)[1])[0])
    cosine_save_dir = os.path.join(cosine_dir,
                                   os.path.splitext(
                                       os.path.split(fname)[1])[0])
    duration_save_dir = os.path.join(duration_dir,
                                     os.path.splitext(
                                       os.path.split(fname)[1])[0])
    if not os.path.exists(traj_save_dir):
        os.mkdir(traj_save_dir)
    if not os.path.exists(cosine_save_dir):
        os.mkdir(cosine_save_dir)
    if not os.path.exists(duration_save_dir):
        os.mkdir(duration_save_dir)
    traj_name = os.path.join(traj_save_dir, "%s.txt" % (bact))
    cosine_name = os.path.join(cosine_save_dir, '%s.txt' % (bact))
    run_log_name = os.path.join(duration_save_dir, 'run_%s.txt' % (bact))
    tumble_log_name = os.path.join(duration_save_dir, 'tumble_%s.txt' % (bact))
    if os.path.exists(traj_name) and os.path.exists(cosine_name)\
        and os.path.exists(run_log_name) and os.path.exists(tumble_log_name)\
            and append:
        print("Value prexists, not recalulating")
        return [traj_name, cosine_name, run_log_name, tumble_log_name]
    start = time.time()
    bacterium = Bacterium(fname)
    bacterium.Complete()
    save_tup = (bacterium.time, bacterium.displacement,
                bacterium.vectors_cartesian)
    export = np.hstack(save_tup)
    np.savetxt(traj_name, export, fmt='%+.5e', delimiter='\t')
    cosine_array = bacterium.run_run_cosines
    np.savetxt(cosine_name, cosine_array, fmt='%+.8e', delimiter='\t')
    run_log = bacterium.run_log
    np.savetxt(run_log_name, run_log, fmt='%d')
    tumble_log = bacterium.tumble_log
    np.savetxt(tumble_log_name, tumble_log, fmt='%d')
    end = time.time()
    elapsed = end-start
    print("Finished Config:\t%s \t %s \tTime taken %f s" % (
        os.path.split(fname)[1], bact, elapsed))
    return [traj_name, cosine_name, run_log_name, tumble_log_name]


class Bacteria:

    def __init__(self):
        self.config = {}
        self.bacterium = {}
        self.cosines = {}
        self.config_path = {}
        self.run_log = {}
        self.tumble_log = {}

    def Import(self, config_dir, traj_dir, cosine_dir, duration_dir):
        for entry in os.scandir(config_dir):
            if entry.path.endswith('.in', -3):
                self.config[os.path.splitext(os.path.split(entry.path)
                                             [1])[0]] = Variables(entry.path)
        for entry in os.scandir(traj_dir):
            if entry.is_dir():
                self.bacterium[os.path.split(entry)[1]] = {}
                for traj_file in os.scandir(entry):
                    self.bacterium[os.path.split(entry)[1]][
                        os.path.split(os.path.splitext(traj_file)[0])[1]]\
                        = traj_file.path
        for entry in os.scandir(cosine_dir):
            if entry.is_dir():
                self.cosines[os.path.split(entry)[1]] = {}
                for cosine_file in os.scandir(entry):
                    self.cosines[os.path.split(entry)[1]][
                        os.path.split(os.path.splitext(cosine_file)[0])[1]]\
                        = cosine_file.path
        for entry in os.scandir(duration_dir):
            if entry.is_dir():
                self.run_log[os.path.split(entry)[1]] = {}
                self.tumble_log[os.path.split(entry)[1]] = {}
                for log_file in os.scandir(entry):
                    if os.path.split(log_file)[1].startswith('run'):
                        key = os.path.splitext(
                            os.path.split(log_file)[1])[0].split('_')[1]
                        self.run_log[os.path.split(entry)[1]][
                            key] = log_file.path
                    elif os.path.split(log_file)[1].startswith('tumble'):
                        key = os.path.splitext(
                            os.path.split(log_file)[1])[0].split('_')[1]
                        self.tumble_log[os.path.split(entry)[1]][
                            key] = log_file.path

    def ConfigSweep_Parallel(self, config_dir, traj_dir, cosine_dir,
                             duration_dir,
                             repeats, threads, append):
        with Parallel(n_jobs=threads) as parallel:
            schedule_array = []
            digits = int(np.ceil(np.log10(repeats+1)))
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
                for entry in os.scandir(duration_dir):
                    if entry.is_dir():
                        for duration_file in os.scandir(entry):
                            os.remove(duration_file)
                    os.rmdir(entry)
            for entry in os.scandir(config_dir):
                if entry.path.endswith('.in', -3):
                    self.config[os.path.splitext(os.path.split(entry.path)
                                                 [1])[0]]\
                        = Variables(entry.path)
                    self.config_path[os.path.splitext(os.path.split(entry.path)
                                                      [1])[0]] = entry.path
            for key in self.config.keys():
                self.bacterium[key] = {}
                self.cosines[key] = {}
                self.run_log[key] = {}
                self.tumble_log[key] = {}
                for i in range(repeats):
                    schedule = ['', '', '']
                    schedule[0] = key
                    bact_iter = str(i)
                    while len(bact_iter) < digits:
                        bact_iter = '0'+bact_iter
                    schedule[1] = 'bact'+bact_iter
                    schedule[2] = self.config_path[key]
                    schedule_array.append(schedule)
            out = parallel(delayed(SingleRun)(schedule_array[i][2],
                                              schedule_array[i][1],
                                              traj_dir, cosine_dir,
                                              duration_dir, append)
                           for i in range(len(schedule_array)))
            for i in range(len(schedule_array)):
                self.bacterium[schedule_array[i][0]][
                    schedule_array[i][1]] = out[i][0]
                self.cosines[schedule_array[i][0]][
                    schedule_array[i][1]] = out[i][1]
                self.run_log[schedule_array[i][0]][
                    schedule_array[i][1]] = out[i][2]
                self.tumble_log[schedule_array[i][0]][
                    schedule_array[i][1]] = out[i][3]
