# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 16:46:45 2019

@author: henry
"""
import numpy as np
from math import sqrt, ceil
import datetime
import os
# &&
def buildBinomial(n,t):
    return np.random.binomial(t, 0.5, (n,3))
# Builds array of (n,3) random binomial outcomes based on B(t, 0.5). 
# Represents total steps taken in positive direction.

def subtractMean(k,t): 
    return k-(t/2)
# Subtracts the t/2 from previous outcome to give steps taken in postive/negative direction

def stepToDistance(k,l):
    return k*l
# Converts step count to displacement

def addTime(k,s):
    time = np.full((len(k),1), s)
    return np.hstack((k,time))
# adds time step to array

def linearDiffusion(n, t, l, s):
    k = buildBinomial(n,t)
    k = subtractMean(k,t)
    k = stepToDistance(k,l)
    k = addTime(k,s)
    return k
# Completes all four of the above steps sequentially. Returns completed array

def diffusionVars(m, T, dc):
    p = m/6.02e23
    v = sqrt(1.38e-23*T/p)
    l = 2*dc/v
    r = v/l
    t = 1/r
    return [p,v,l,r,t]
# Builds diffusion variables for runDiffusion from temperature, Diffusion coefficient and molecular mass

def timeVars(dv, rt, ts):
    n = ceil(rt/ts)
    t = ceil(dv[3]*ts/2)*2
    s = dv[4]*t
    return [n,t,s]
# Builds runtime variables based on diffusion variables and required run time and time precision

def runDiffusion(dv, tv):
    return linearDiffusion(tv[0],tv[1],dv[2],tv[2])
# Runs linear diffusiion based of prebuilt diffusion and time variables

def linearDiffusionExportOld(k):
    total = list(k)
    n=len(total)
    total.insert(0,np.zeros(4))
    for x in range(n):
        total[x+1]=total[x+1]+total[x]
    return np.asarray(total)
# Sums contents of array based on previous values and outputs complete diffusion path.

def linearDiffusionExport(k):
    return np.cumsum(k, axis=0)

def guidedDiffusion():
    print("Welcome to the guided Linear Particle Diffusion position 4vector generator!")
    while True:
        try:
            m = float(input("Please enter the molecular mass of the particle (kg/mol) :"))
            if m > 0:
                break
            else:
                print("Error: Negative Mass not possible")
        except ValueError:
            print("Error: That is not a numerical input")
    
    while True:
        try:
            dc = float(input("Please enter the Diffusion Constant (m^2/s) :"))
            if dc > 0:
                break
            else:
                print("Error: Concentration not within scope yet")
        except ValueError:
            print("Error: That is not a numerical input")
    
    while True:
        try:
            T = float(input("Please enter the temperature (K) :"))
            if T > 0:
                break
            else:
                print("Error: Negative temperature not possible")
        except ValueError:
            print("Error: That is not a numerical input")
    
    while True:
        try:
            rt = float(input("Please enter the desired run time (s) :"))
            if rt > 0:
                break
            else:
                print("Error: Negative run times are prohibited")
        except ValueError:
            print("Error: That is not a numerical input")
    
    while True:
        try:
            ts = float(input("Please enter the desired diffusion interval (s) :"))
            if ts > 0:
                break
            else:
                print("Error: Negative diffusion intervals are prohibited")
        except ValueError:
            print("Error: That is not a numerical input")
        
    dv = diffusionVars(m, T, dc)
    tv = timeVars(dv, rt, ts)
    k = runDiffusion(dv,tv)
    return linearDiffusionExport(k)
# Provides guided method for building a diffusion output

def linearDiffusionSave(results=np.zeros(1)):
    if results.any() == False:
        results=guidedDiffusion()
    i = 0
    while os.path.exists("LinearDiffusion "+str(datetime.date.today())+" "+str(i)+".out"):
        i = i+1
        
    fileName = "LinearDiffusion "+str(datetime.date.today())+" "+str(i)+".out"
    np.savetxt(fileName, results, delimiter = '\t')
# saves output to text file in work directory.

def chunkedDiffusionBuild(m, T, dc, rt, ts, tChunk):
    dv = diffusionVars(m, T, dc)
    tv = timeVars(dv, rt, ts)
    chunks = ceil(rt/tChunk)
    chunkN = ceil(tChunk/ts)
    seed = np.zeros((chunks, 1), dtype=int)
    results = np.zeros((chunks, 4))
    for x in range(chunks):
        seed[x] = np.random.randint(2**31-1)
        np.random.seed(seed[x])
        k = linearDiffusion(chunkN, tv[1], dv[2], tv[2])
        results[x] = np.sum(k, axis=0)
    output = np.hstack((seed, results))  
    return output, [dv, tv, m, T, dc, rt, ts, tChunk, chunkN]

def chunkedDiffusionRender(k, tStart, tEnd):
    data = k[0]
    var = k[1]
    dv = var[0]
    tv = var[1]
    chunkN=int(var[8])
    del k, var
    x = 0
    seeds,position,time=np.split(data, [1,4], axis=1)
    del data
    while True:
        if np.sum(time[:x], axis=0) > tStart:
            iStart = x-1
            print(iStart)
            break
        x=x+1
    while True:
        if np.sum(time[:x], axis=0) > tEnd:
            iEnd = x
            print(iEnd)
            break
        x=x+1
    posStart = np.sum(position[:iStart], axis=0)
    timeStart = np.sum(time[:iStart], axis=0)
    results=np.hstack((posStart, timeStart))
    for i in range(iStart, iEnd):
        np.random.seed(int(seeds[i]))
        p = linearDiffusion(chunkN, tv[1], dv[2], tv[2])
        results = np.vstack((results, p))
    return results

def headingGen(n): # Generates random starting heading for n particles
    k = np.random.rand(n, 2)
    
    
        
        
        

    
    