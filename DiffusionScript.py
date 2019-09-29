# -*- coding: utf-8 -*-
from math import sqrt
from math import factorial as fact
from math import pi
from math import e
from math import exp
import random
from random import random as rand
import datetime
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import csv

def SimpleDiffusion(T=297, mass=14.3, diffusionConstant=1E-10, n=10000): #Temperature (K), Molecularmass (kg), Diffusion Constant (m^2/s) number of steps
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
        particlePos.append([0,0,0,particlePos[x][3]+stepTime])
        for y in range(3):
            if rand() > 0.5:
                particlePos[x+1][y]=particlePos[x][y]+stepLength
            else:
                particlePos[x+1][y]=particlePos[x][y]-stepLength
    particlePos.insert(0, [currentSeed, T, mass, diffusionConstant, instantaeousVelocity, particleMass, stepLength, stepRate, stepTime])
    i = 0
    while os.path.exists("SimpleDiffusion "+str(datetime.date.today())+" "+str(i)+".csv"):
        i = i+1
    
    fileName = "SimpleDiffusion "+str(datetime.date.today())+" "+str(i)+".csv"
    f = open(fileName, 'w+', newline='')
    linewriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for x in range(len(particlePos)):
        linewriter.writerow(particlePos[x])
    f.close()
    #return particlePos
            
def SimplePlot(fileName=''):
    if fileName == '':
        i=0
        while os.path.exists("SimpleDiffusion "+str(datetime.date.today())+" "+str(i)+".csv"):
            i = i+1
        fileName = "SimpleDiffusion "+str(datetime.date.today())+" "+str(i-1)+".csv"
    f = open(fileName, 'r')
    linereader=csv.reader(f)
    particleValues=list(linereader)
    particleVariables = particleValues.pop(0)
    plotValues = [[],[],[]]
    for x in range(len(particleValues)):
        #print(x)
        for y in range(3):
            plotValues[y].append(float(particleValues[x][y]))
    fig = plt.figure(figsize=(20,20))
    ax = plt.axes(projection='3d')
    ax.plot3D(plotValues[0], plotValues[1], plotValues[2])
    plt.savefig("SimpleDiffusion "+str(datetime.date.today())+" "+str(i-1)+".pdf", bbox_inches='tight')
    # return plotValues
    
def GaussDiffusion(T=297, mass=14.3, diffusionConstant=1E-10, time=1, timestep=1e-6):
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
        particlePos.append([0,0,0,particlePos[x][3]+stepTime])
        for y in range(3):
            if rand() > 0.5:
                particlePos[x+1][y]=particlePos[x][y]+stepLength
            else:
                particlePos[x+1][y]=particlePos[x][y]-stepLength
    particlePos.insert(0, [currentSeed, T, mass, diffusionConstant, instantaeousVelocity, particleMass, stepLength, stepRate, stepTime])
    i = 0
    while os.path.exists("GaussDiffusion "+str(datetime.date.today())+" "+str(i)+".csv"):
        i = i+1
    
    fileName = "GaussDiffusion "+str(datetime.date.today())+" "+str(i)+".csv"
    f = open(fileName, 'w+', newline='')
    linewriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for x in range(len(particlePos)):
        linewriter.writerow(particlePos[x])
    f.close()

def BinomialDistribution(n=1000, p=0.5):
    values = [(fact(n)/(fact(x)*fact(n-x))*(p**x)*((1-p)**(n-x))) for x in range(n+1)]
    return values

def GaussianDistribution(n=1000, p=0.5):
    mean = n*p
    variance = (n*p*(1-p))**2
    values = [(1/sqrt(2*pi*variance))*exp(-((x-mean)**2)/(2*(variance))) for x in range(n+1)]
    return values