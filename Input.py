#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 22:04:35 2020

@author: henry
"""

import Config
import Interactive

class Variables:
    def __init__(self,fname="",interactive=0):
        if fname == "" and interactive == 1:
            print("Entering Interactive Input Mode \n")
            config = Interactive.Input()
        elif fname == "":
            Config.Default()
            self.success = 1
            print("Then retry function using your custom configuration.")
            print("Or run with 'interactive=1' to input variables in the console.")
        else:
            config = Config.GetConfig(fname)
            if config.sections() == ['phys', 'env', 'time', 'bact']:
                self.phys = config['phys']
                self.env = config['env']
                self.time = config['time']
                self.bact = config['bact']
            else:
                print("Error: Config file not formatted correctly.")
                print("Please recreate options from default config and try again.")
                self.success = 1
    
    def Extract(self):
        return 0
                
            
            
            