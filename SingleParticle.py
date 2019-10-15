# -*- coding: utf-8 -*-

from math import sqrt, ceil
from scipy.special import erfinv
from numpy import random
import time
import os
from numba import jit, njit, prange
import numpy as np
import datetime

def SimpleDiffusionStep(particlePos,stepTime, stepLength):
    particlePos[3] = particlePos[3]+stepTime
    for y in range(3):
        if rand() > 0.5:
            particlePos[y]=particlePos[y]+stepLength
        else:
            particlePos[y]=particlePos[y]-stepLength
    return particlePos

def SimpleDiffusion(T=297, mass=14.3, diffusionConstant=1E-10, n=10000):
    particlePos = [[0,0,0,0]] # x,y,z,t
    particleMass = mass/6.02E23
    boltzmann = 1.38E-23
    kT = boltzmann*T
    instantaeousVelocity = sqrt(kT/particleMass)
    stepLength = 2*diffusionConstant/instantaeousVelocity
    stepRate = instantaeousVelocity/stepLength
    stepTime = 1/stepRate
    currentSeed = datetime.datetime.now()
    random.seed(a=currentSeed, version=2)
    for x in range(n):
        particlePos.append(SimpleDiffusionStep(particlePos[x], stepTime, stepLength))
    particlePos.insert(0, [currentSeed, T, mass, diffusionConstant, instantaeousVelocity, particleMass, stepLength, stepRate, stepTime])
    return particlePos

def SimpleDiffusionExport(T=297, mass=14.3, diffusionConstant=1E-10, n=10000, results=False):
    if results == False:
        results=SimpleDiffusion(T, mass, diffusionConstant, n)
    i = 0
    while os.path.exists("SimpleDiffusion "+str(datetime.date.today())+" "+str(i)+".out"):
        i = i+1
    
    fileName = "SimpleDiffusion "+str(datetime.date.today())+" "+str(i)+".out"
    f = open(fileName, 'w+')
    for p in range(len(results)):
        for q in range(len(results[p])):
            f.write(str(results[p][q])+' ')
        f.write('\n')
    f.close()

def GaussDiffusionStep(particlePos, gaussMean, gaussDev, gaussTime, stepLength):
    particlePos[3]=particlePos[3]+gaussTime
    for y in range(3):
        stepCount = (erfinv(2*random()-1)*(stdDev*sqrt(2))+mean) - gaussMean
        particlePos[y] = particlePos[y] + stepCount*stepLength
    return particlePos

def GaussDiffusion(T=297, mass=14.3, diffusionConstant=1E-10, runTime=1, timeStep=1e-6):
    particleMass = mass/6.02E23
    boltzmann = 1.38E-23
    kT = boltzmann*T
    instantaeousVelocity = sqrt(kT/particleMass)
    stepLength = 2*diffusionConstant/instantaeousVelocity
    stepRate = instantaeousVelocity/stepLength
    stepTime = 1/stepRate
    currentSeed = datetime.datetime.now()
    random.seed(a=currentSeed, version=2)
    n = ceil(runTime/timeStep)
    gaussStep = ceil((stepRate*timeStep)/2)*2
    gaussTime = gaussStep*stepTime
    gaussMean = gaussStep/2
    gaussVar = gaussStep/4
    gaussDev = sqrt(gaussVar)
    particlePos = [[0,0,0,0] for x in range(n+1)]
    for x in range(n):
        particlePosCurrent = GaussDiffusionStep(particlePos[x], gaussMean, gaussDev, gaussTime, stepLength)
        particlePos[x+1] = [particlePosCurrent[y] for y in range(4)]
    particlePos.insert(0, [currentSeed, T, mass, diffusionConstant, instantaeousVelocity, particleMass, stepLength, stepRate, stepTime])
    return particlePos

def GaussDiffusionExport(T=297, mass=14.3, diffusionConstant=1E-10, runTime=1, timeStep=1e-6, results=False):
    if results == False:
        results=GaussDiffusion(T, mass, diffusionConstant, runTime, timeStep)
    i = 0
    while os.path.exists("GaussDiffusion "+str(datetime.date.today())+" "+str(i)+".out"):
        i = i+1
    
    fileName = "GaussDiffusion "+str(datetime.date.today())+" "+str(i)+".out"
    f = open(fileName, 'w+')
    for p in range(len(results)):
        for q in range(len(results[p])):
            f.write(str(results[p][q])+' ')
        f.write('\n')
    f.close()

@njit(parallel=True)
def BinomialDiffusionStep(trials, prob, meanStep, binomTime, stepLength):
    particlePos = np.zeros(4)
    particlePos[3] = binomTime
    for y in prange(3):
        stepCount = random.binomial(trials, prob) - meanStep
        particlePos[y] = stepCount*stepLength
    return particlePos

@njit(parallel=True)
def BinomialDiffusion(T=297, mass=14.3, diffusionConstant=1E-10, runTime=1.0, timeStep=1e-6):
    particleMass = mass/6.02E23
    boltzmann = 1.38E-23
    kT = boltzmann*T
    instantaeousVelocity = sqrt(kT/particleMass)
    stepLength = 2*diffusionConstant/instantaeousVelocity
    stepRate = instantaeousVelocity/stepLength
    stepTime = 1/stepRate
    #currentSeed = int(time.time())
    #random.seed(currentSeed)
    n = ceil(runTime/timeStep)
    trials = ceil((stepRate*timeStep)/2)*2
    #print(trials)
    binomTime = trials*stepTime
    meanStep = trials/2
    prob = 0.5
    particlePos = np.zeros((n,4))
    #print("Initialised")
    p = 0
    for x in prange(n):
        particlePos[x] = BinomialDiffusionStep(trials, prob, meanStep, binomTime, stepLength)
        p = p+1
        print(p)
    #particlePos.insert(0, [currentSeed, T, mass, diffusionConstant, instantaeousVelocity, particleMass, stepLength, stepRate, stepTime])
    return particlePos

@jit
def BinomialDiffusionExport(T=297, mass=14.3, diffusionConstant=1E-10, runTime=1e-3, timeStep=1e-6, results=False):
    if results == False:
        results=BinomialDiffusion(T, mass, diffusionConstant, runTime, timeStep)
    i = 0
    export = [list(results[0:x:1].sum(axis=0)) for x in range(len(results))]
    
    while os.path.exists("BinomialDiffusion "+str(datetime.date.today())+" "+str(i)+".out"):
        i = i+1

    fileName = "BinomialDiffusion "+str(datetime.date.today())+" "+str(i)+".out"
    f = open(fileName, 'w+')
    for p in range(len(export)):
        for q in range(len(export[p])):
            f.write(str(export[p][q])+' ')
        f.write('\n')
    f.close()