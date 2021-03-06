#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:43:54 2020

@author: henry
"""
import numpy as np
import os

class LDValues:
    def __init__(self, variables):
        if not variables.run_behaviour:
            self.LD = False
            return
        else:
            self.LD = True
        self.archaea = variables.archaea_mode
        self.run_speed = variables.run_force/variables.frictional_drag_linear
        self.diffusive = variables.diffusive
        self.diff_rot = variables.diffusion_constant_rotational
        self.simstep = variables.base_time
        if self.diffusive:
            alpha = np.sqrt(4*self.diff_rot*self.simstep)
            self.tau_B = self.simstep/(1-np.cos(alpha))
        self.avg_tumble = 0.0 # Values for these are set during analysis sequence
        self.avg_run_duration = 0.0
        self.avg_tumble_duration = 0.0
        self.tau_A = 0.0
    def LDCalc(self):
        if not self.LD:
            self.LD_Diff = -1.0
            return
        if self.archaea:
            self.tau_A = self.avg_run_duration/2
        else:
            self.tau_A = self.avg_run_duration**2/((self.avg_run_duration+self.avg_tumble_duration)
                                                *(1-np.cos(self.avg_tumble)))
        if self.diffusive:
            self.Tau = (self.tau_A**-1 + self.tau_B**-1)**-1
        else:
            self.Tau = self.tau_A
        self.LD_Diff = (1/3)*self.run_speed**2*self.Tau

def LoadValues(fname, request):
    values = np.loadtxt(fname, delimiter='\t')
    values = np.delete(values, 0, 0)
    values = np.swapaxes(values, 0, 1)
    if request == 'displacement':
        return np.swapaxes(values[1:4], 0, 1)
    elif request == 'heading':
        return np.swapaxes(values[4:7], 0, 1)
    else:
        return values


def LoadCosines(fname):
    values = np.loadtxt(fname, delimiter='\t')
    return values


def LoadDurations(fname):
    values = np.loadtxt(fname).astype(int)
    return values


def TauCalc(variables):
    sample_total = int(np.floor(np.log2(variables.sim_time
                                        / variables.base_time)))
    tau = np.zeros(sample_total)
    tau_curr = variables.base_time
    for i in range(sample_total):
        tau[i] = tau_curr
        tau_curr = tau_curr*2
    return tau


def TauCalcHR(variables):
    return np.arange(10, (variables.sim_time/2)+1, 5)


def MSD(disp, tau_i, sample_total):
    size = int(np.floor(sample_total/tau_i))
    delta = np.zeros((size, 3))
    for i in range(size):
        delta[i] = np.sum(disp[(tau_i*i):((i+1)*tau_i)], axis=0)
    delta = delta**2
    delta = np.sum(delta, axis=1)
    delta_mean = np.mean(delta)
    return delta_mean


def MSD_Rot(vect, tau_i, sample_total, key):
    with np.errstate(invalid='ignore'):
        size = int(np.floor(sample_total/tau_i)-1)
        if size == 0:
            return -1
        delta = np.zeros(size)
        for i in range(size):
            delta[i] = np.dot(vect[i*tau_i], vect[(i+1)*tau_i])
        angles = np.arccos(delta)
        angles = angles**2
        angles_mean = np.nanmean(angles)
        return angles_mean


def Linear(bacterium, variables):
    linear = LoadValues(bacterium, 'displacement')
    tau = TauCalc(variables)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/variables.base_time))
        results[i] = MSD(linear, tau_i, variables.sample_total)
    return results


def LinearHighRange(bacterium, variables):
    linear = LoadValues(bacterium, 'displacement')
    tau = np.arange(10, (variables.sim_time/2)+1, 5)
    tau_i = np.round(tau/variables.base_time).astype(int)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        results[i] = MSD(linear, tau_i[i], variables.sample_total)
    return results


def Rotational(bacterium, variables):
    key = os.path.split(bacterium)[1]
    rotational_vect = LoadValues(bacterium, 'heading')
    tau = TauCalc(variables)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/variables.base_time))
        results[i] = MSD_Rot(rotational_vect, tau_i,
                             variables.sample_total, key)
    return results


def RunRunAngles(cosines):
    cosine_array = LoadCosines(cosines)
    angle_array = np.arccos(cosine_array)
    return angle_array


def GetTimes(duration, variables):
    duration_array = LoadDurations(duration)
    time_array = duration_array*variables.base_time
    return time_array
