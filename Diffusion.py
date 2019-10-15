# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 16:46:45 2019

@author: henry
"""
import numpy as np
from math import sqrt, ceil
import datetime
import os

        
def buildBinomial(n,t):
    return np.random.binomial(t, 0.5, (n,3))

def subtractMean(k,t):
    return k-(t/2)

def stepToDistance(k,l):
    return k*l

def addTime(k,s):
    time = np.full((len(k),1), s)
    return np.hstack((k,time))

def linearDiffusion(n, t, l, s):
    k = buildBinomial(n,t)
    k = subtractMean(k,t)
    k = stepToDistance(k,l)
    k = addTime(k,s)
    return k

def diffusionVars(m, T, dc):
    p = m/6.02e23
    v = sqrt(1.38e-23*T/p)
    l = 2*dc/v
    r = v/l
    t = 1/r
    return [p,v,l,r,t]

def timeVars(dv, rt, ts):
    n = ceil(rt/ts)
    t = ceil(dv[3]*ts/2)*2
    s = dv[4]*t
    return [n,t,s]

def runDiffusion(dv, tv):
    return linearDiffusion(tv[0],tv[1],dv[2],tv[2])

def linearDiffusionExport(k):
    total = list(k)
    n=len(total)
    total.insert(0,np.zeros(4))
    for x in range(n):
        total[x+1]=total[x+1]+total[x]
    return np.asarray(total)

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

def linearDiffusionSave(results):
    if results == False:
        results=guidedDiffusion()
    i = 0
    while os.path.exists("LinearDiffusion "+str(datetime.date.today())+" "+str(i)+".out"):
        i = i+1
        
    fileName = "LinearDiffusion "+str(datetime.date.today())+" "+str(i)+".out"
    np.savetxt(fileName, results, delimiter = '\t')
    
    
    