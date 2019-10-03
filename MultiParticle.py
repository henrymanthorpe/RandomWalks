# -*- coding: utf-8 -*-
import os
import datetime
from SingleParticle import GaussDiffusion, GaussDiffusionStep

def MultiParticleGaussDiffusion(T=297, mass=14.3, diffusionConstant=1E-10, runTime=1e-3, timeStep=1e-6, particleTotal = 3):
    particlePos = [GaussDiffusion(T, mass, diffusionConstant, runTime, timeStep) for x in range(particleTotal)]
    for x in range(particleTotal):
        particlePos[x].insert(0, x)
    return particlePos


def MultiParticleGaussDiffusionStep(particlePos, gaussMean, gaussDev, gaussTime, stepLength):
    for x in range(len(particlePos)):
        particlePos[x] = GaussDiffusionStep(particlePos, gaussMean, gaussDev, gaussTime, stepLength)
    return particlePos

def MultiParticleGaussDiffusionExport(T=297, mass=14.3, diffusionConstant=1E-10, runTime=1e-3, timeStep=1e-6, particleTotal = 3, results=False):
    if results == False:
        results = MultiParticleGaussDiffusion(T, mass, diffusionConstant, runTime, timeStep, particleTotal)
    i = 0
    while os.path.exists("GaussDiffusion "+str(datetime.date.today())+" "+str(i)+".out"):
        i = i+1
    
    fileName = "GaussDiffusion "+str(datetime.date.today())+" "+str(i)+".out"
    f = open(fileName, 'w+')
    for p in range(len(results)):
        f.write(str(results[p].pop(0)))
        f.write('\n')
        for q in range(len(results[p])):
            for r in range(len(results[p][q])):
                f.write(str(results[p][q][r])+' ')
            f.write('\n')
        f.write('\n')
    f.close()
    