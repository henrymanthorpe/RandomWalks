#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 17:46:37 2020

@author: henry
"""
import os
import numpy as np
from numpy.random import Generator, PCG64, SeedSequence
from Simulate import Normalise, MakeRotationQuaternion, Tumble
import matplotlib.pyplot as plt
from joblib import Parallel, delayed


def MultiDist(n, mu, sigma):
    rand_gen = Generator(PCG64(SeedSequence()))
    dist_1 = rand_gen.exponential(1, n)
    mu_array = np.full(n, mu)
    mu_array = mu_array*dist_1
    dist_2 = rand_gen.normal(mu_array, sigma)
    plt.hist(dist_2, bins='auto')
    plt.show()


def ReExport(traj_dir):
    for entry in os.scandir(traj_dir):
        if not entry.is_file():
            continue
        entry_data = np.loadtxt(entry, delimiter='\t')
        if entry_data.shape[1] == 10:
            entry_data = np.delete(entry_data, [4, 5, 6], 1)
        elif entry_data.shape[1] == 7:
            pass
        else:
            print("Error at %s, incorrect data values (columns = %d)" % (
                entry, entry_data.shape[2]))
            continue
        entry_split = os.path.split(entry)[-1]
        entry_split = entry_split.split('_')
        save_dir = os.path.join(traj_dir, entry_split[0])
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        save_file = os.path.join(save_dir, entry_split[1])
        np.savetxt(save_file, entry_data, fmt='%+.5e', delimiter='\t')
        os.remove(entry)


def TumbleAlignmentCheck(n, t):
    with Parallel(n_jobs=t) as parallel:
        rand_gen = Generator(PCG64(SeedSequence()))
        vect_initial = [1, 0, 0]
        tau_alpha = rand_gen.exponential(0.1, 10000)
        tumble_alpha = rand_gen.normal(0, tau_alpha)
        spin_alpha = rand_gen.uniform(0, 2*np.pi, n)
        tumble_beta = 1
        spin_beta = rand_gen.uniform(0, 2*np.pi, n)
        vect_mid = parallel(delayed(Tumble)(tumble_alpha[i], spin_alpha[i],
                                            vect_initial)
                            for i in range(n))
        vect_final = parallel(delayed(Tumble)(tumble_beta, spin_beta[i],
                                              vect_mid[i])
                              for i in range(n))
    return vect_final
