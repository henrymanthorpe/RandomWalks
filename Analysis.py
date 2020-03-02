#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:43:54 2020

@author: henry
"""
import numpy as np


def TauCalc(bacterium):
    sample_total = int(np.floor(np.log2(bacterium.vars.sim_time
                                        / bacterium.vars.base_time)))
    tau = np.zeros(sample_total)
    tau_curr = bacterium.vars.base_time
    for i in range(sample_total):
        tau[i] = tau_curr
        tau_curr = tau_curr*2
    return tau


def MSD(disp, tau_i, sample_total):
    size = int(np.floor(sample_total/tau_i))
    delta = np.zeros((size, 3))
    for i in range(size):
        delta[i] = np.sum(disp[(tau_i*i):((i+1)*tau_i)], axis=0)
    delta = delta**2
    delta = np.sum(delta, axis=1)
    delta_mean = np.mean(delta)
    return delta_mean


def MSD_Rot(vect, tau_i, sample_total):
    size = int(np.floor(sample_total/tau_i)-1)
    if size == 0:
        return -1
    delta = np.zeros(size)
    for i in range(size):
        delta[i] = np.dot(vect[i*tau_i], vect[(i+1)*tau_i])
    delta = np.arccos(delta)
    delta = delta**2
    delta_mean = np.mean(delta)
    return delta_mean


def LinearDiffusion(bacterium):
    linear = bacterium.linear_diffusion
    tau = TauCalc(bacterium)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/bacterium.vars.base_time))
        results[i] = MSD(linear, tau_i, bacterium.vars.sample_total)
    return results


def RotationalDiffusion(bacterium):
    rotational_vect = bacterium.vectors_cartesian_diffusion
    tau = TauCalc(bacterium)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/bacterium.vars.base_time))
        results[i] = MSD_Rot(rotational_vect, tau_i,
                             bacterium.vars.sample_total)
    return results


def LinearMotility(bacterium):
    linear = bacterium.displacement
    tau = TauCalc(bacterium)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/bacterium.vars.base_time))
        results[i] = MSD(linear, tau_i, bacterium.vars.sample_total)
    return results


def RotationalMotility(bacterium):
    rotational_vect = bacterium.vectors_cartesian
    tau = TauCalc(bacterium)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/bacterium.vars.base_time))
        results[i] = MSD_Rot(rotational_vect, tau_i,
                             bacterium.vars.sample_total)
    return results



    