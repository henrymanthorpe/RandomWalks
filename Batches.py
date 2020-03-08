#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 22:55:08 2020

@author: henry
"""
import os
import Interactive
import configparser
import numpy as np
from Config import GetConfig

def MakeBatch():
    batch_dir = input('Enter Batch Directory Name :')
    config_dir = os.path.join(batch_dir,'configs')
    if not os.path.exists(batch_dir):
        os.mkdir(batch_dir)
        os.mkdir(config_dir)
    elif not os.path.exists(config_dir):
        os.mkdir(config_dir)
    base_config = input('Enter Filename of config file :')
    section, key = input('Enter section and key name :').split()
    config = GetConfig(base_config)
    start, stop, step_num = input('Enter start value, stop value, and number of steps :').split()
    start = float(start)
    stop = float(stop)
    step_num = int(step_num)
    step_val = (stop-start)/step_num
    digits = int(np.ceil(np.log10(step_num+1)))
    for i in range(step_num):
        config.set(section,key,str(start+(i*step_val)))
        file_iter = str(i)
        while len(file_iter) < digits:
            file_iter = '0'+file_iter
        fname = key+'_'+file_iter+'.in'
        save_name = os.path.join(config_dir,fname)
        with open(save_name,'w') as f:
            config.write(f)
            f.close()



