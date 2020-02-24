#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 10:56:16 2020

@author: henry
"""
from joblib import Parallel, delayed
from Simulate import Bacterium
import os

def SingleRun(fname):
    bacterium = Bacterium(fname)
    bacterium.Rotational()
    bacterium.Complete()
    return bacterium


class Bacteria:
    def __init__(self):
        self.config = {}
        self.bacterium = {}
        self.test_num = 0
        
    def Repeat(self, fname, repeats):
        self.test_num += 1
        self.config['config'+str(self.test_num)] = fname
        self.bacterium['set'+str(self.test_num)] = {}
        for i in range(repeats):
            self.bacterium['set'+str(self.test_num)]['bact'+str(i)] = SingleRun(fname)

    def ConfigSweep(self, configdir, repeats):
        for entry in os.scandir(configdir):
            self.Repeat(entry.path, repeats)

    def ConfigSweep_Parallel(self, config_dir, repeats, threads):
        with Parallel(n_jobs=threads) as parallel:
            self.schedule_array = []
            for entry in os.scandir(config_dir):
                if entry.path.endswith('.in',-3):
                    self.config[os.path.splitext(os.path.split(entry.path)[-1])[0]] = entry.path
                    self.bacterium[os.path.splitext(os.path.split(entry.path)[-1])[0]] = {}
                    for i in range(repeats):
                        self.schedule_array.append(['','',''])
                        self.schedule_array[-1][0] = os.path.splitext(os.path.split(entry.path)[-1])[0]
                        self.schedule_array[-1][1] = 'bact'+str(i)
                        self.schedule_array[-1][2] = entry.path
            out = parallel(delayed(SingleRun)(self.schedule_array[i][2]) for i in range(len(self.schedule_array)))
            for i in range(len(self.schedule_array)):
                self.bacterium[self.schedule_array[i][0]][self.schedule_array[i][1]] = out[i]
                
                
                
                
           
            

        
        