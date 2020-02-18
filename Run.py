#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 10:56:16 2020

@author: henry
"""

from Simulate import Bacterium
import os

class Bacteria:
    def __init__(self):
        self.config = {}
        self.bacterium = {}
        self.test_num = 0
        
    def Repeat(self, fname, repeats):
        self.config_number += 1
        self.config['config'+str(self.test_num)] = fname
        self.bacterium['set'+str(self.test_num)] = {}
        for i in range(repeats):
            self.bacterium['set'+str(self.test_num)]['bact'+str(i)] = Bacterium(fname)
            self.bacterium['set'+str(self.test_num)]['bact'+str(i)].Complete()
        
    
    def ConfigSweep(self, configdir, repeats):
        for entry in os.scandir(configdir):
            self.Repeat(entry.path, repeats)
    
        
        