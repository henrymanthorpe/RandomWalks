#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:12:28 2020

@author: henry
"""

import os
import Analysis
import numpy as np
import PyGnuplot as gp


class Graphing:

    def __init__(self, bacteria, graph_dir, plot_dir):
        self.bacteria = bacteria
        self.results = {}
        self.fit_linear = {}
        self.stats_linear = {}
        self.plots = {}
        self.graph_dir = graph_dir
        self.plot_dir = plot_dir
        for entry in os.scandir(plot_dir):
            os.remove(entry.path)

    def BacteriaPaths(self):
        gp.c("reset")
        gp.c("set ticslevel 0")
        gp.c("set view equal xyz")
        gp.c("set terminal pngcairo enhanced size 1600,1200 font 'ariel, 14'")
        for key in self.bacteria.bacterium.keys():
            output = os.path.join(self.graph_dir, key+'_path.png')
            gp.c('set output "'+output+'"')
            plot_string = 'splot'
            for bact in self.bacteria.bacterium[key].keys():
                temp_out = self.bacteria.bacterium[
                    key][bact].total_displacement
                graph_out = np.swapaxes(temp_out, 0, 1)
                dat_name = os.path.join(self.plot_dir,
                                        str(key)+str(bact)+'path.dat')
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "' + dat_name\
                    + '" u 1:2:3 with lines,'
            gp.c(plot_string)

    def BacteriaHeading(self):
        gp.c("reset")
        gp.c("set ticslevel 0")
        gp.c("set view equal xyz")
        gp.c("set terminal pngcairo enhanced size 1600,1200 font 'ariel, 14'")
        for key in self.bacteria.bacterium.keys():
            output = os.path.join(self.graph_dir, key+'_heading.png')
            gp.c('set output "'+output+'"')
            plot_string = 'splot'
            for bact in self.bacteria.bacterium[key].keys():
                temp_out = self.bacteria.bacterium[key][bact].vectors_cartesian
                graph_out = np.swapaxes(temp_out, 0, 1)
                dat_name = os.path.join(self.plot_dir,
                                        str(key)+str(bact)+'heading.dat')
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "' + dat_name\
                    + '" u 1:2:3 with lines,'
            gp.c(plot_string)

    def BrownianDiffusionConstants(self, mean=True):
        gp.c('reset')
        gp.c('set logscale xy 10')
        gp.c('set xlabel "{/Symbol t} (s)"')
        gp.c('set ylabel "MSD (m^2)"')
        gp.c('set key top left')
        g_title = '"Analysis of Linear Diffusion Mean Squared Displacement"'
        gp.c('set title ' + g_title)
        gp.c("set terminal pngcairo enhanced size 1600,1200 font 'ariel, 14'")
        for key in self.bacteria.bacterium.keys():
            output = os.path.join(self.graph_dir, key+'brownian_linear.png')
            gp.c('set output "'+output+'"')
            plot_string = 'plot'
            tau = Analysis.TauCalc(self.bacteria.config[key])
            p = len(tau)
            q = len(self.bacteria.bacterium[key])
            results_array = np.zeros((q, p))
            i = 0
            for bact in self.bacteria.bacterium[key].keys():
                graph_out = Analysis.LinearDiffusion(
                    self.bacteria.bacterium[key][bact])
                results_array[i] = graph_out
                graph_out = np.vstack((graph_out, tau))
                dat_name = os.path.join(self.plot_dir,
                                        key + bact + '_br_msd_lin.dat')
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "' + dat_name\
                    + '" u 2:1 with points title "' + str(bact) + ' MSD",'
                i = i + 1
            mean_results = np.mean(results_array, axis=0)
            if q > 1:
                std_dev = np.std(results_array, axis=0)
                std_error = std_dev/np.sqrt(q)
            else:
                std_error = np.ones(len(tau))
            self.results[key + 'linear_brownian'] = np.vstack(
                (mean_results, tau, std_error))
            dat_name = os.path.join(self.plot_dir,
                                    key + bact + '_br_msd_lin_mean.dat')
            gp.s(self.results[key+'linear_brownian'], dat_name)
            plot_string = plot_string + ' "' + dat_name\
                + '" u 2:1:3 with yerrorbars'\
                + 'title "Mean Averaged MSD w/Standard Errors",'
            x = self.results[key+'linear_brownian'][1]
            y = self.results[key+'linear_brownian'][0]
            weight = self.results[key+'linear_brownian'][2]
            self.fit_linear[key], self.stats_linear[key]\
                = np.polynomial.polynomial.polyfit(
                    x, y, 1, full=True, w=(1/weight))
            gp.c('a = '+str(self.fit_linear[key][0]))
            gp.c('b = '+str(self.fit_linear[key][1]))
            gp.c('f(x) = b*x')
            plot_string = plot_string\
                + ' f(x) title "Linear Regression Fit, grad='\
                + str(self.fit_linear[key][1]) + '"'
            gp.c(plot_string)
        gp.c('set ylabel "MSD ({/Symbol q}^2)"')
        g_title = '"Analysis of Rotational Diffusion'\
            + ' Mean Squared Displacement"'
        gp.c('set title ' + g_title)
        for key in self.bacteria.bacterium.keys():
            output = os.path.join(self.graph_dir,
                                  key+'brownian_rotational.png')
            gp.c('set output "'+output+'"')
            plot_string = 'plot'
            tau = Analysis.TauCalc(self.bacteria.config[key])
            p = len(tau)
            q = len(self.bacteria.bacterium[key])
            results_array = np.zeros((q, p))
            i = 0
            for bact in self.bacteria.bacterium[key].keys():
                graph_out = Analysis.RotationalDiffusion(
                    self.bacteria.bacterium[key][bact])
                results_array[i] = graph_out
                graph_out = np.vstack((graph_out, tau))
                dat_name = os.path.join(self.plot_dir,
                                        key + bact + '_br_msd_rot.dat')
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "' + dat_name\
                    + '" u 2:1 with points title "' + str(bact) + ' MSD",'
                i = i + 1
            mean_results = np.mean(results_array, axis=0)
            if q > 1:
                std_dev = np.std(results_array, axis=0)
                std_error = std_dev/np.sqrt(q)
            else:
                std_error = np.ones(len(tau))
            self.results[key+'rotational_brownian'] = np.vstack(
                (mean_results, tau, std_error))
            dat_name = os.path.join(self.plot_dir,
                                    key + bact + '_br_msd_rot_mean.dat')
            gp.s(self.results[key+'rotational_brownian'], dat_name)
            plot_string = plot_string + ' "' + dat_name\
                + '" u 2:1:3 with yerrorbars'\
                + ' title "Mean Averaged MSD w/Standard Errors",'
            x = self.results[key+'rotational_brownian'][1]
            y = self.results[key+'rotational_brownian'][0]
            weight = self.results[key+'rotational_brownian'][2]
            self.fit_linear[key], self.stats_linear[key]\
                = np.polynomial.polynomial.polyfit(
                    x, y, 1, full=True, w=(1/weight))
            gp.c('a = '+str(self.fit_linear[key][0]))
            gp.c('b = '+str(self.fit_linear[key][1]))
            gp.c('f(x) = b*x')
            plot_string = plot_string\
                + ' f(x) title "Linear Regression Fit, grad='\
                + str(self.fit_linear[key][1]) + '"'
            gp.c(plot_string)

    def MotilityDiffusionConstants(self, mean=True):
        gp.c('reset')
        gp.c('set logscale xy 10')
        gp.c('set xlabel "{/Symbol t} (s)"')
        gp.c('set ylabel "MSD (m^2)"')
        gp.c('set key top left')
        g_title = '"Analysis of Linear Motility Mean Squared Displacement"'
        gp.c('set title ' + g_title)
        gp.c("set terminal pngcairo enhanced size 1600,1200 font 'ariel, 14'")
        for key in self.bacteria.bacterium.keys():
            output = os.path.join(self.graph_dir, key+'_motility_linear.png')
            gp.c('set output "'+output+'"')
            plot_string = 'plot'
            tau = Analysis.TauCalc(self.bacteria.config[key])
            gp.c('set xrange ['+str(tau.min()*0.75)+':'+str(tau.max()*1.5)+']')
            p = len(tau)
            q = len(self.bacteria.bacterium[key])
            results_array = np.zeros((q, p))
            i = 0
            for bact in self.bacteria.bacterium[key].keys():
                graph_out = Analysis.Linear(
                    self.bacteria.bacterium[key][bact],
                    self.bacteria.config[key])
                results_array[i] = graph_out
                graph_out = np.vstack((graph_out, tau))
                dat_name = os.path.join(self.plot_dir,
                                        key + bact + '_mot_msd_lin.dat')
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "' + dat_name\
                    + '" u 2:1 with points title "' + str(bact) + ' MSD",'
                i = i + 1
            mean_results = np.mean(results_array, axis=0)
            if q > 1:
                std_dev = np.std(results_array, axis=0)
                std_error = std_dev/np.sqrt(q)
            else:
                std_error = np.ones(len(tau))
            self.results[key+'linear'] = np.vstack(
                (mean_results, tau, std_error))
            dat_name = os.path.join(self.plot_dir,
                                    key + bact + '_mot_msd_lin_mean.dat')
            gp.s(self.results[key+'linear'], dat_name)
            plot_string = plot_string + ' "' + dat_name\
                + '" u 2:1:3 with yerrorbars'\
                + ' title "Mean Averaged MSD w/Standard Errors",'
            gp.c(plot_string)
        gp.c('set ylabel "MSD ({/Symbol q}^2)"')
        g_title = '"Analysis of Rotational Motility Mean Squared Displacement"'
        gp.c('set title ' + g_title)
        for key in self.bacteria.bacterium.keys():
            output = os.path.join(self.graph_dir,
                                  key+'_motility_rotational.png')
            gp.c('set output "'+output+'"')
            plot_string = 'plot'
            tau = Analysis.TauCalc(self.bacteria.config[key])
            gp.c('set xrange ['+str(tau.min()*0.75)+':'+str(tau.max()*1.5)+']')
            p = len(tau)
            q = len(self.bacteria.bacterium[key])
            results_array = np.zeros((q, p))
            i = 0
            for bact in self.bacteria.bacterium[key].keys():
                graph_out = Analysis.Rotational(
                    self.bacteria.bacterium[key][bact],
                    self.bacteria.config[key])
                results_array[i] = graph_out
                graph_out = np.vstack((graph_out, tau))
                dat_name = os.path.join(self.plot_dir,
                                        key + bact + 'mot_msd_rot.dat')
                gp.s(graph_out, dat_name)
                plot_string = plot_string + ' "' + dat_name\
                    + '" u 2:1 with points title "' + str(bact) + 'MSD",'
                i = i + 1
            mean_results = np.mean(results_array, axis=0)
            if q > 1:
                std_dev = np.std(results_array, axis=0)
                std_error = std_dev/np.sqrt(q)
            else:
                std_error = np.ones(len(tau))
            self.results[key+'rotational'] = np.vstack(
                (mean_results, tau, std_error))
            dat_name = os.path.join(self.plot_dir,
                                    key + bact + '_mot_msd_rot_mean.dat')
            gp.s(self.results[key+'rotational'], dat_name)
            plot_string = plot_string + ' "' + dat_name\
                + '" u 2:1:3 with yerrorbars'\
                + ' title "Mean Averaged MSD w/Standard Errors",'
            gp.c(plot_string)
        gp.c('set ylabel "MSD (m^2)')
        g_title = '"Linear Regression of Mean Squared Displacement"'
        gp.c('set title ' + g_title)
        for key in self.bacteria.bacterium.keys():
            tau = Analysis.TauCalc(self.bacteria.config[key])
            x = self.results[key+'linear'][1]
            y = self.results[key+'linear'][0]
            weight = self.results[key+'linear'][2]
            run_duration\
                = self.bacteria.config[key].run_duration_mean
            tau_split = np.searchsorted(tau, run_duration, 'left')
            self.fit_linear[key+'low'], self.stats_linear[key+'low']\
                = np.polynomial.polynomial.polyfit(
                    x[:tau_split], y[:tau_split], 1,
                    full=True, w=1/weight[:tau_split])
            self.fit_linear[key+'high'], self.stats_linear[key+'high']\
                = np.polynomial.polynomial.polyfit(
                    x[tau_split:], y[tau_split:], 1,
                    full=True, w=1/weight[tau_split:])
            output = os.path.join(self.graph_dir,
                                  key+'_motility_linear_fit.png')
            gp.c('set output "'+output+'"')
            plot_string = 'plot'
            gp.c('set xrange ['+str(x.min()*0.75)+':'+str(x.max()*1.5)+']')
            graph_out = np.vstack((x, y, weight))
            dat_name = os.path.join(self.plot_dir,
                                    key + bact + '_mot_lin_fit.dat')
            gp.s(graph_out, dat_name)
            plot_string = plot_string + ' "' + dat_name\
                + '" u 1:2:3 with yerrorbars'\
                + ' title "Mean Averaged MSD w/Standard Errors",'
            gp.c('a = '+str(self.fit_linear[key+'low'][1]))
            gp.c('f(x) = a*x')
            plot_string = plot_string + ' f(x) title "Low = '\
                + str(self.fit_linear[key+'low'][1])+'",'
            gp.c('b = '+str(self.fit_linear[key+'high'][1]))
            gp.c('g(x) = b*x')
            plot_string = plot_string + ' g(x) title "High = '\
                + str(self.fit_linear[key+'high'][1])+'"'
            gp.c(plot_string)
