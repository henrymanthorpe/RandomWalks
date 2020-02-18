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
        
    

def LinearDiffusion(bacterium):
    linear = np.cumsum(bacterium.linear_diffusion, axis=0)
    tau = TauCalc(bacterium)
    sample_total = int(np.floor(np.log2(bacterium.vars.sim_time/bacterium.vars.base_time)))
    results = np.zeros(sample_total)
    run_total = bacterium.vars.sample_total
    for i in range(sample_total):
        sample_size = int(np.floor(bacterium.vars.sim_time/tau[i]))
        tau_i = int(np.floor(run_total/sample_size))
        for y in range(3):
            results_stack = np.zeros(sample_size-1)
            for x in range(sample_size-1):
                results_stack[x] = linear[(x+1)*tau_i][y]-linear[x*tau_i][y]
            results_stack_2 = results_stack**2
            results[i] = results[i] + np.mean(results_stack_2)
    results = np.vstack((results,tau))
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
    results = np.vstack((results,tau))
    return results

def LinearMotility(bacterium):
    linear = np.cumsum(bacterium.total_displacement, axis=0)
    tau = TauCalc(bacterium)
    sample_total = int(np.floor(np.log2(bacterium.vars.sim_time/bacterium.vars.base_time)))
    results = np.zeros(sample_total)
    run_total = bacterium.vars.sample_total
    for i in range(sample_total):
        sample_size = int(np.floor(bacterium.vars.sim_time/tau[i]))
        tau_i = int(np.floor(run_total/sample_size))
        for y in range(3):
            results_stack = np.zeros(sample_size-1)
            for x in range(sample_size-1):
                results_stack[x] = linear[(x+1)*tau_i][y]-linear[x*tau_i][y]
            results_stack_2 = results_stack**2
            results[i] = results[i] + np.mean(results_stack_2)
    results = np.vstack((results,tau))
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
    results = np.vstack((results,tau))
    return results
    