#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:43:54 2020

@author: henry
"""
import numpy as np

def TauCalc(bacterium):
    sample_total = int(np.floor(np.log2(bacterium.vars.sim_time/bacterium.vars.base_time)))
    tau = np.zeros(sample_total)
    tau_curr = bacterium.vars.base_time
    for i in range(sample_total):
        tau[i] = tau_curr
        tau_curr = tau_curr*2
    return tau
        
def MSD(disp,tau_i,sample_total):
    size = int(np.floor(sample_total/tau_i))
    delta = np.zeros((size,3))
    for i in range(0,size*tau_i,tau_i):
        delta[int(i/tau_i)] = np.sum(disp[i:(i+tau_i)],axis=0)
    delta = delta**2
    delta = np.sum(delta,axis=1)
    delta_mean = np.mean(delta)
    return delta_mean

def MSD_Rot(vect,tau_i,sample_total):
    size=int(np.floor(sample_total/tau_i))
    delta = np.zeros((size,2,3))
    



def LinearDiffusion(bacterium):
    linear = bacterium.linear_diffusion
    tau = TauCalc(bacterium)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/bacterium.vars.base_time))
        results[i] = MSD(linear,tau_i,bacterium.vars.sample_total)
    return results

def RotationalDiffusion(bacterium):
    rotational_vect = bacterium.vectors_cartesian_diffusion
    tau = TauCalc(bacterium)
    sample_total = int(np.floor(np.log2(bacterium.vars.sim_time/bacterium.vars.base_time)))
    results = np.zeros(sample_total)
    run_total = bacterium.vars.sample_total
    for i in range(sample_total):
        sample_size = int(np.floor(bacterium.vars.sim_time/tau[i]))
        tau_i = int(np.floor(run_total/sample_size))
        results_stack = np.zeros(sample_size-1)
        for x in range(sample_size-1):
            results_stack[x] = np.dot(rotational_vect[(x+1)*tau_i],rotational_vect[x*tau_i])
            results_stack[x] = np.arccos(results_stack[x])
        results_stack_2 = results_stack**2
        results[i] = np.mean(results_stack_2)
    return results

def LinearMotility(bacterium):
    linear = bacterium.displacement
    tau = TauCalc(bacterium)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/bacterium.vars.base_time))
        results[i] = MSD(linear,tau_i,bacterium.vars.sample_total)
    return results

def RotationalMotility(bacterium):
    rotational_vect = bacterium.vectors_cartesian
    tau = TauCalc(bacterium)
    sample_total = int(np.floor(np.log2(bacterium.vars.sim_time/bacterium.vars.base_time)))
    results = np.zeros(sample_total)
    run_total = bacterium.vars.sample_total
    for i in range(sample_total):
        sample_size = int(np.floor(bacterium.vars.sim_time/tau[i]))
        tau_i = int(np.floor(run_total/sample_size))
        results_stack = np.zeros(sample_size-1)
        for x in range(sample_size-1):
            results_stack[x] = np.dot(rotational_vect[(x+1)*tau_i],rotational_vect[x*tau_i])
            results_stack[x] = np.arccos(results_stack[x])
        results_stack_2 = results_stack**2
        results[i] = np.mean(results_stack_2)
    return results


    