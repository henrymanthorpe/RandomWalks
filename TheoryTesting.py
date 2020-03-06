#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 17:46:37 2020

@author: henry
"""

import numpy as np
from numpy.random import Generator, PCG64, SeedSequence
import matplotlib.pyplot as plt


def MultiDist(n, mu, sigma):
    rand_gen = Generator(PCG64(SeedSequence()))
    dist_1 = rand_gen.exponential(1,n)
    mu_array = np.full(n,mu)
    mu_array = mu_array*dist_1
    dist_2 = rand_gen.normal(mu_array,sigma)
    plt.hist(dist_2,bins='auto')
    plt.show()
