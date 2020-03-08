#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:43:54 2020

@author: henry
"""
import numpy as np


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

def TauCalc(variables):
    sample_total = int(np.floor(np.log2(variables.sim_time
                                        / variables.base_time)))
    tau = np.zeros(sample_total)
    tau_curr = variables.base_time
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


def Linear(bacterium, variables):
    linear = LoadValues(bacterium, 'displacement')
    tau = TauCalc(variables)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/variables.base_time))
        results[i] = MSD(linear, tau_i, variables.sample_total)
    return results


def Rotational(bacterium, variables):
    rotational_vect = LoadValues(bacterium, 'heading')
    tau = TauCalc(variables)
    results = np.zeros(len(tau))
    for i in range(len(tau)):
        tau_i = int(np.round(tau[i]/variables.base_time))
        results[i] = MSD_Rot(rotational_vect, tau_i,
                             variables.sample_total)
    return results


        # graph_out = Analysis.LinearDiffusion(
        # self.bacteria.bacterium[key][bact])
        # results_array[i] = graph_out
        # graph_out = np.vstack((graph_out, tau))
        # dat_name = os.path.join(self.plot_dir,
        #                         key + bact + '_br_msd_lin.dat')
        # gp.s(graph_out, dat_name)
        # plot_string = plot_string + ' "' + dat_name\
        #     + '" u 2:1 with points title "' + str(bact) + ' MSD",'
        #         i = i + 1

# def LinearMotility(bacterium):
#     linear = bacterium.displacement
#     tau = TauCalc(bacterium)
#     results = np.zeros(len(tau))
#     for i in range(len(tau)):
#         tau_i = int(np.round(tau[i]/bacterium.vars.base_time))
#         results[i] = MSD(linear, tau_i, bacterium.vars.sample_total)
#     return results


# def RotationalMotility(bacterium):
#     rotational_vect = bacterium.vectors_cartesian
#     tau = TauCalc(bacterium)
#     results = np.zeros(len(tau))
#     for i in range(len(tau)):
#         tau_i = int(np.round(tau[i]/bacterium.vars.base_time))
#         results[i] = MSD_Rot(rotational_vect, tau_i,
#                              bacterium.vars.sample_total)
#     return results
