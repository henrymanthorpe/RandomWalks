#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 10:56:16 2020

@author: henry
"""
from joblib import Parallel, delayed
from Simulate import Bacterium
import os
from Config import Default

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
    
    def Repeat_Parallel(self, fname, repeats, cores):
        self.test_num += 1
        self.config['config'+str(self.test_num)] = fname
        self.bacterium['set'+str(self.test_num)] = {}
        with Parallel(n_jobs=cores) as parallel:
            out = parallel(delayed(SingleRun)(fname) for i in range(repeats))
        for i in range(repeats):
            self.bacterium['set'+str(self.test_num)]['bact'+str(i)] = out[i]
            
    def ConfigSweep_Parallel(self, configdir, repeats, threads):
        with Parallel(n_jobs=threads) as parallel:
            for entry in os.scandir(configdir):
                if entry.path.endswith('.in',-3):
                    self.test_num += 1
                    self.config['config'+str(self.test_num)] = entry.path
                    self.bacterium['set'+str(self.test_num)] = {}
                    out = parallel(delayed(SingleRun)(entry.path) for i in range(repeats))
                    for i in range(repeats):
                        self.bacterium['set'+str(self.test_num)]['bact'+str(i)] = out[i]
        if self.test_num == 0:
            Default(configdir)
        
            

        
        