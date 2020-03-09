#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  8 21:48:15 2020

@author: henry
"""

import os
import numpy as np
from joblib import Parallel, delayed


def VisifyData(fname, vis_dir, vis_name):
    save_name = os.path.join(vis_dir, "%s.txt" % (vis_name))
    data = np.loadtxt(fname, delimiter='\t')
    data = np.swapaxes(data, 0, 1)
    data = data[0:4]
    data[1:4] = data[1:4]*1e6
    data = np.swapaxes(data, 0, 1)
    if not data[0][1:4].all():
        data[0][1:4] = np.random.uniform(50, 300, 3)
    data = np.swapaxes(data, 0, 1)
    data[1:4] = np.cumsum(data[1:4], axis=1)
    data = np.vstack((data, data[1:4]))
    data = np.swapaxes(data, 0, 1)
    np.savetxt(save_name, data, fmt='%.8e', delimiter='\t')
    return


def VisifyExport(batch, vis_dir, threads):
    with Parallel(n_jobs=threads) as parallel:
        for entry in os.scandir(vis_dir):
            if entry.is_dir():
                for vis_file in os.scandir(entry):
                    os.remove(vis_file)
                os.rmdir(entry)
        schedule_array = []
        for key in batch.bacterium.keys():
            vis_path = os.path.join(vis_dir, key)
            if not os.path.exists(vis_path):
                os.mkdir(vis_path)
            for bact in batch.bacterium[key].keys():
                schedule = ['', '', '']
                schedule[0] = batch.bacterium[key][bact]
                schedule[1] = os.path.join(vis_dir, key)
                schedule[2] = bact
                schedule_array.append(schedule)
        parallel(delayed(VisifyData)(schedule_array[i][0],
                                     schedule_array[i][1],
                                     schedule_array[i][2])
                 for i in range(len(schedule_array)))
