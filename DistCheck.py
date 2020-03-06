#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 13:36:30 2020

@author: henry
"""


import numpy as np
from numpy.random import Generator, PCG64, SeedSequence
import matplotlib.pyplot as plt
from TumbleDistribution import Fit

def DecayExpCheck(mu):
    rand_gen = Generator(PCG64(SeedSequence()))
    dist_data = rand_gen.exponential(mu, 10000)
    plt.yscale('log')
    plt.hist(dist_data,bins='auto',density=True)
    x = np.linspace(0,10,1000)
    y = np.exp(-x)
    plt.plot(x,y,'-')
    plt.show()


def TumbleDistCheck(poly):
    rand_gen = Generator(PCG64(SeedSequence()))
    p = Fit(poly)
    dist_data = p(rand_gen.random(1000000))
    plt.hist(dist_data, bins='auto',density=True)
    print(np.mean(dist_data))
    plt.show()

