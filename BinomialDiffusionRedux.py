# -*- coding: utf-8 -*-

import numpy as np
from math import sqrt, ceil
from numba import njit, prange, float64, int32

@njit(parallel=True)
def DiffusionStep(trials, prob, mS, sL, n, bT):
    particlePos = np.random.binomial(trials, prob, size=3*n).reshape((n,3))
        #print(x)
    #particlePos = particlePos - mS
    #particlePos = particlePos * sL
    #results = np.full((n,4), bT)
    #results[:,:-1]=particlePos
    return particlePos

@njit
def Diffusion(T, mass, diffConst, rT, tS):
    pMass = mass/6.02e23
    kT = 1.38e-23*T
    iV = sqrt(kT/pMass)
    sL = 2*diffConst/iV
    sR = iV/sL
    sT = 1/sR
    n = ceil(rT/tS)
    trials = ceil((sR*tS)/2)*2
    bT = sT*trials
    mS = trials/2
    prob = 0.5
    results = DiffusionStep(trials, prob, mS, sL, n, bT)
    particle = [np.sum(results[:x], axis=0) for x in prange(n)]
    return particle

@njit
def BinomTest(trials, n):
    return np.random.binomial(trials, 0.5, n)
