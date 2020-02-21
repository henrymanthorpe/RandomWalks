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

class Graphing:
    def __init__(self, bacteria):
        self.bacteria = bacteria
        self.results = {}
        self.fit_linear = {}
        self.stats_linear = {}

    def BacteriaPaths(self):
        gp.c("reset")
        gp.c("set ticslevel 0")
        gp.c("set view equal xyz")
        term = 0
        for key in self.bacteria.bacterium.keys():
            gp.c("set terminal qt "+str(term))
            plot_string = 'splot'
            for bact in self.bacteria.bacterium[key].keys():
                temp_out = self.bacteria.bacterium[key][bact].total_displacement
                graph_out = np.swapaxes(temp_out, 0, 1)
                dat_name = 'results/'+str(key)+str(bact)+'path.dat'
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "'+dat_name+'" u 1:2:3 with lines,'
            gp.c(plot_string)
            term = term+1
                
    def BacteriaHeading(self):
        gp.c("reset")
        gp.c("set ticslevel 0")
        gp.c("set view equal xyz")
        term = 0
        for key in self.bacteria.bacterium.keys():
            gp.c("set terminal qt "+str(term))
            plot_string = 'splot'
            for bact in self.bacteria.bacterium[key].keys():
                temp_out = self.bacteria.bacterium[key][bact].vectors_cartesian
                graph_out = np.swapaxes(temp_out, 0, 1)
                dat_name = 'results/'+str(key)+str(bact)+'heading.dat'
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "'+dat_name+'" u 1:2:3 with lines,'
            gp.c(plot_string)
            term = term+1
        
    def BrownianDiffusionConstants(self, mean=True):
        gp.c('reset')
        term = 0
        gp.c('set logscale xy 10')
        gp.c('set xlabel "{/Symbol t} (s)"')
        gp.c('set ylabel "MSD (m^2)"')
        gp.c('set title "Analysis of Linear Diffusion Mean Squared Displacement"')
        for key in self.bacteria.bacterium.keys():
            gp.c("set terminal qt "+str(term))
            plot_string = 'plot'
            diffusion_constant_linear = self.bacteria.bacterium[key]['bact0'].vars.diffusion_constant_linear
            tau = Analysis.TauCalc(self.bacteria.bacterium[key]['bact0'])
            graph_out = 6*diffusion_constant_linear*tau
            graph_out = np.vstack((graph_out,tau))
            dat_name = 'results/'+str(key)+'exp_msd_lin.dat'
            gp.s(graph_out, dat_name)
            plot_string = plot_string + ' "' + dat_name + '" u 2:1 with lines title "Expected MSD",'
            gp.c('a = '+str(6*diffusion_constant_linear))
            gp.c('f(x) = a*x')
            plot_string = plot_string + ' f(x) title "f(x) = 6D{/Symbol t}",'
            p = len(tau)
            q = len(self.bacteria.bacterium[key])
            results_array = np.zeros((q,p))
            i=0
            for bact in self.bacteria.bacterium[key].keys():
                graph_out = Analysis.LinearDiffusion(self.bacteria.bacterium[key][bact])
                results_array[i] = graph_out
                graph_out = np.vstack((graph_out, tau))
                dat_name = 'results/'+str(key)+str(bact)+'msd_lin.dat'
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "'+dat_name+'" u 2:1 with points title "'+str(bact)+' MSD",'
                i=i+1
            mean_results = np.mean(results_array, axis=0)
            std_dev = np.std(results_array, axis=0)
            std_error = std_dev/np.sqrt(q)
            self.results[key+'linear_brownian'] = np.vstack((mean_results,tau,std_error))
            dat_name = 'results/'+str(key)+'msd_lin__brownian_mean.dat'
            gp.s(self.results[key+'linear_brownian'], dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 2:1:3 with yerrorbars title "Mean Averaged MSD w/Standard Errors",'
            x = self.results[key+'linear_brownian'][1]
            y = self.results[key+'linear_brownian'][0]
            weight = self.results[key+'linear_brownian'][2]
            self.fit_linear[key], self.stats_linear[key] = np.polynomial.polynomial.polyfit(x,y,1,full=True,w=(1/weight))
            gp.c('a = '+str(self.fit_linear[key][0]))
            gp.c('b = '+str(self.fit_linear[key][1]))
            gp.c('f(x) = b*x')
            plot_string = plot_string + ' f(x) title "Linear Regression Fit"'
            gp.c(plot_string)
            term = term+1
            plot_string = 'plot'
            gp.c("set terminal qt "+str(term))
            #gp.c("unset logscale xy")
            gp.c('set logscale x 10')
            mean_diff = mean_results/tau
            graph_out = np.vstack((mean_diff,tau))
            dat_name = 'results/'+str(key)+'msd_lin_brownian_diff.dat'
            gp.s(graph_out,dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 2:1 with points title "6D",'
            gp.c('a='+str(diffusion_constant_linear))
            gp.c('f(x) = 6*a')
            plot_string = plot_string + ' f(x)'
            gp.c(plot_string)
        # gp.c('set ylabel "MSD ({/Symbol q}^2)"')
        # gp.c('set title "Analysis of Rotational Diffusion Mean Squared Displacement"')
        # for key in self.bacteria.bacterium.keys():
        #     gp.c("set terminal qt "+str(term))
        #     plot_string = 'plot'
        #     diffusion_constant_rotational = self.bacteria.bacterium[key]['bact0'].vars.diffusion_constant_rotational
        #     tau = Analysis.TauCalc(self.bacteria.bacterium[key]['bact0'])
        #     graph_out = 4*diffusion_constant_rotational*tau
        #     graph_out = np.vstack((graph_out,tau))
        #     dat_name = 'results/'+str(key)+'exp_msd_rot.dat'
        #     gp.s(graph_out, dat_name)
        #     plot_string = plot_string + ' "' + dat_name + '" u 2:1 with lines title "Expected MSD",'
        #     for bact in self.bacteria.bacterium[key].keys():
        #         self.bacteria.bacterium[key][bact].Rotational()
        #         graph_out = Analysis.RotationalDiffusion(self.bacteria.bacterium[key][bact])
        #         graph_out = np.vstack((graph_out, tau))
        #         dat_name = 'results/'+str(key)+str(bact)+'msd_rot.dat'
        #         gp.s(graph_out, dat_name)
        #         plot_string = plot_string + ' "'+dat_name+'" u 2:1 with points title "'+str(bact)+' MSD",'
        #     gp.c(plot_string)
        #     term = term+1
            
    def MotilityDiffusionConstants(self, mean=True):
        gp.c('reset')
        term = 0
        gp.c('set logscale xy 10')
        gp.c('set xlabel "{/Symbol t} (s)"')
        gp.c('set ylabel "MSD (m^2)"')
        gp.c('set key top left')
        gp.c('set title "Analysis of Linear Motility Mean Squared Displacement"')
        
        for key in self.bacteria.bacterium.keys():
            gp.c("set terminal qt "+str(term))
            plot_string = 'plot'
            tau = Analysis.TauCalc(self.bacteria.bacterium[key]['bact0'])
            gp.c('set xrange ['+str(tau.min()*0.75)+':'+str(tau.max()*1.5)+']')
            p = len(tau)
            q = len(self.bacteria.bacterium[key])
            results_array = np.zeros((q,p))
            i = 0
            for bact in self.bacteria.bacterium[key].keys():
                graph_out = Analysis.LinearMotility(self.bacteria.bacterium[key][bact])
                results_array[i] = graph_out
                graph_out = np.vstack((graph_out, tau))
                dat_name = 'results/'+str(key)+str(bact)+'msd_lin.dat'
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "'+dat_name+'" u 2:1 with points title "'+str(bact)+' MSD",'
                i=i+1
            mean_results = np.mean(results_array, axis=0)
            std_dev = np.std(results_array, axis=0)
            std_error = std_dev/np.sqrt(q)
            self.results[key+'linear'] = np.vstack((mean_results,tau,std_error))
            dat_name = 'results/'+str(key)+'msd_lin_mean.dat'
            gp.s(self.results[key+'linear'], dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 2:1:3 with yerrorbars title "Mean Averaged MSD w/Standard Errors",'
            gp.c(plot_string)
            term = term+1
        gp.c('set ylabel "MSD ({/Symbol q}^2)"')
        gp.c('set title "Analysis of Rotational Motility Mean Squared Displacement"')
        for key in self.bacteria.bacterium.keys():
            gp.c("set terminal qt "+str(term))
            plot_string = 'plot'
            tau = Analysis.TauCalc(self.bacteria.bacterium[key]['bact0'])
            gp.c('set xrange ['+str(tau.min()*0.75)+':'+str(tau.max()*1.5)+']')
            p = len(tau)
            q = len(self.bacteria.bacterium[key])
            results_array = np.zeros((q,p))
            i = 0
            for bact in self.bacteria.bacterium[key].keys():
                graph_out = Analysis.RotationalMotility(self.bacteria.bacterium[key][bact])
                results_array[i] = graph_out
                graph_out = np.vstack((graph_out, tau))
                dat_name = 'results/'+str(key)+str(bact)+'msd_rot.dat'
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "'+dat_name+'" u 2:1 with points title "'+str(bact)+' MSD",'
                i = i+1
            mean_results = np.mean(results_array, axis=0)
            std_dev = np.std(results_array, axis=0)
            std_error = std_dev/np.sqrt(q)
            self.results[key+'rotational'] = np.vstack((mean_results,tau,std_error))
            dat_name = 'results/'+str(key)+'msd_rot_mean.dat'
            gp.s(self.results[key+'rotational'], dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 2:1:3 with yerrorbars title "Mean Averaged MSD w/Standard Errors",'
            gp.c(plot_string)
            term = term+1
        
        gp.c('set ylabel "MSD (m^2)')
        gp.c('set title "Linear Regression  of Linear Motility Mean Squared Displacement"')
        for key in self.bacteria.bacterium.keys():
            x = self.results[key+'linear'][1]
            y = self.results[key+'linear'][0]
            weight = self.results[key+'linear'][2]
            self.fit_linear[key], self.stats_linear[key] = np.polynomial.polynomial.polyfit(x,y,1,full=True)
            gp.c("set terminal qt "+str(term))
            plot_string = 'plot'
            gp.c('set xrange ['+str(x.min()*0.75)+':'+str(x.max()*1.5)+']')
            graph_out = np.vstack((x,y,weight))
            dat_name = 'results/'+str(key)+'lin_fit.dat'
            gp.s(graph_out,dat_name)
            plot_string = plot_string + ' "'+dat_name+'" u 1:2:3 with yerrorbars title "Mean Averaged MSD w/Standard Errors",'
            gp.c('a = '+str(self.fit_linear[key][0]))
            gp.c('b = '+str(self.fit_linear[key][1]))
            gp.c('f(x) = b*x')
            plot_string = plot_string + ' f(x) title "Linear Regression Fit"'
            gp.c(plot_string)
            term = term+1
            
            
            
        
    
        
