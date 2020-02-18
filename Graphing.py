#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:12:28 2020

@author: henry
"""

from Run import Bacteria
import Analysis
import numpy as np
import PyGnuplot as gp

def BacteriaPaths(bacteria):
    gp.c("reset")
    gp.c("set ticslevel 0")
    gp.c("set view equal xyz")
    term = 0
    for key in bacteria.bacterium.keys():
        gp.c("set terminal qt "+str(term))
        plot_string = 'splot'
        for bact in bacteria.bacterium[key].keys():
            temp_out = bacteria.bacterium[key][bact].total_displacement
            graph_out = np.swapaxes(temp_out, 0, 1)
            dat_name = str(key)+str(bact)+'.dat'
            gp.s(graph_out, dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 1:2:3 with lines,'
        gp.c(plot_string)
        term = term+1
            
def BacteriaHeading(bacteria):
    gp.c("reset")
    gp.c("set ticslevel 0")
    gp.c("set view equal xyz")
    term = 0
    for key in bacteria.bacterium.keys():
        gp.c("set terminal qt "+str(term))
        plot_string = 'splot'
        for bact in bacteria.bacterium[key].keys():
            temp_out = bacteria.bacterium[key][bact].vectors_cartesian
            graph_out = np.swapaxes(temp_out, 0, 1)
            dat_name = str(key)+str(bact)+'.dat'
            gp.s(graph_out, dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 1:2:3 with lines,'
        gp.c(plot_string)
        term = term+1
    
def BrownianDiffusionConstants(bacteria):
    gp.c('reset')
    term = 0
    gp.c('set logscale xy 10')
    gp.c('set xlabel "{/Symbol t} (s)"')
    gp.c('set ylabel "MSD (m^2)"')
    gp.c('set title "Analysis of Linear Diffusion Mean Squared Displacement"')
    for key in bacteria.bacterium.keys():
        gp.c("set terminal qt "+str(term))
        plot_string = 'plot'
        diffusion_constant_linear = bacteria.bacterium[key]['bact0'].vars.diffusion_constant_linear
        tau = Analysis.TauCalc(bacteria.bacterium[key]['bact0'])
        graph_out = 6*diffusion_constant_linear*tau
        graph_out = np.vstack((graph_out,tau))
        dat_name = str(key)+'exp_msd_lin.dat'
        gp.s(graph_out, dat_name)
        plot_string = plot_string + ' "' + dat_name + '" u 2:1 with lines title "Expected MSD",'
        for bact in bacteria.bacterium[key].keys():
            graph_out = Analysis.LinearDiffusion(bacteria.bacterium[key][bact])
            dat_name = str(key)+str(bact)+'msd_lin.dat'
            gp.s(graph_out, dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 2:1 with points title "'+str(bact)+' MSD",'
        gp.c(plot_string)
        term = term+1
    gp.c('set ylabel "MSD ({/Symbol q}^2)"')
    gp.c('set title "Analysis of Rotational Diffusion Mean Squared Displacement"')
    for key in bacteria.bacterium.keys():
        gp.c("set terminal qt "+str(term))
        plot_string = 'plot'
        diffusion_constant_rotational = bacteria.bacterium[key]['bact0'].vars.diffusion_constant_rotational
        tau = Analysis.TauCalc(bacteria.bacterium[key]['bact0'])
        graph_out = 4*diffusion_constant_rotational*tau
        graph_out = np.vstack((graph_out,tau))
        dat_name = str(key)+'exp_msd_rot.dat'
        gp.s(graph_out, dat_name)
        plot_string = plot_string + ' "' + dat_name + '" u 2:1 with lines title "Expected MSD",'
        for bact in bacteria.bacterium[key].keys():
            bacteria.bacterium[key][bact].Rotational()
            graph_out = Analysis.RotationalDiffusion(bacteria.bacterium[key][bact])
            dat_name = str(key)+str(bact)+'msd_rot.dat'
            gp.s(graph_out, dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 2:1 with points title "'+str(bact)+' MSD",'
        gp.c(plot_string)
        term = term+1
        
def MotilityDiffusionConstants(bacteria):
    gp.c('reset')
    term = 0
    gp.c('set logscale xy 10')
    gp.c('set xlabel "{/Symbol t} (s)"')
    gp.c('set ylabel "MSD (m^2)"')
    gp.c('set title "Analysis of Linear Motility Mean Squared Displacement"')
    for key in bacteria.bacterium.keys():
        gp.c("set terminal qt "+str(term))
        plot_string = 'plot'
        diffusion_constant_linear = bacteria.bacterium[key]['bact0'].vars.diffusion_constant_linear
        tau = Analysis.TauCalc(bacteria.bacterium[key]['bact0'])
        graph_out = 6*diffusion_constant_linear*tau
        graph_out = np.vstack((graph_out,tau))
        dat_name = str(key)+'exp_msd_lin.dat'
        gp.s(graph_out, dat_name)
        plot_string = plot_string + ' "' + dat_name + '" u 2:1 with lines title "Diffusion MSD",'
        for bact in bacteria.bacterium[key].keys():
            graph_out = Analysis.LinearMotility(bacteria.bacterium[key][bact])
            dat_name = str(key)+str(bact)+'msd_lin.dat'
            gp.s(graph_out, dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 2:1 with points title "'+str(bact)+' MSD",'
        gp.c(plot_string)
        term = term+1
    gp.c('set ylabel "MSD ({/Symbol q}^2)"')
    gp.c('set title "Analysis of Rotational Motility Mean Squared Displacement"')
    for key in bacteria.bacterium.keys():
        gp.c("set terminal qt "+str(term))
        plot_string = 'plot'
        diffusion_constant_rotational = bacteria.bacterium[key]['bact0'].vars.diffusion_constant_rotational
        tau = Analysis.TauCalc(bacteria.bacterium[key]['bact0'])
        graph_out = 4*diffusion_constant_rotational*tau
        graph_out = np.vstack((graph_out,tau))
        dat_name = str(key)+'exp_msd_rot.dat'
        gp.s(graph_out, dat_name)
        plot_string = plot_string + ' "' + dat_name + '" u 2:1 with lines title "Diffusion MSD",'
        for bact in bacteria.bacterium[key].keys():
            graph_out = Analysis.RotationalMotility(bacteria.bacterium[key][bact])
            dat_name = str(key)+str(bact)+'msd_rot.dat'
            gp.s(graph_out, dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 2:1 with points title "'+str(bact)+' MSD",'
        gp.c(plot_string)
        term = term+1
    
        
