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
from joblib import Parallel, delayed
from scipy.stats import linregress

        

def plotStringSingleFile(size, dat_name, formatting, title):
    plot_string = 'plot'
    for i in range(size):
        plot_string = plot_string\
            + ' "%s" u 1:%d %s %s,' % (dat_name, i+2, formatting, title[i])
    return plot_string


def plotStringMultiFile(size, dat_name, formatting, title):
    plot_string = 'plot'
    for i in range(size):
        plot_string = plot_string\
            + ' "%s" %s %s,' % (dat_name[i], formatting, title[i])
    return plot_string

def plotStringMultiFileWithFit(size, dat_name, formatting, title, grad,
                               grad_title):
    plot_string = 'plot'
    for i in range(size):
        plot_string = plot_string\
            + ' "%s" %s lc %d %s,' % (dat_name[i], formatting, i, title[i])
        plot_string = plot_string\
            + ' %e*x lc %d title "%s",' % (grad[i], i, grad_title[i])
    return plot_string

# %%
class Graphing:

    def __init__(self, bacteria, graph_dir, plot_dir, threads):
        self.bacteria = bacteria
        self.graph_dir = graph_dir
        self.plot_dir = plot_dir
        self.threads = threads
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

    def DiffusionConstants(self):
        with Parallel(n_jobs=self.threads) as parallel:
            self.LDValues = {}
            for key in self.bacteria.bacterium.keys():
                self.LDValues[key] = Analysis.LDValues(self.bacteria.config[key])
# %% Linear - LogLog fullscale
            gp.c('reset')
            gp.c('set logscale xy 10')
            gp.c('set xlabel "{/Symbol t} (s)"')
            gp.c('set ylabel "MSD (m^2)"')
            gp.c('set key top left')
            gp.c("set terminal pngcairo enhanced"
                 + " size 1600,1200 font 'ariel, 14'")
            amalg_dat_name = []
            amalg_titles = []
            for key in self.bacteria.bacterium.keys():
                key_title = self.bacteria.config[key].name
                print('Started: %s \t Linear Analysis' % (key_title))

                output = os.path.join(self.graph_dir,
                                      '%s_linear.png' % (key))
                gp.c('set output "%s"' % (output))
                g_title = 'Analysis of Linear Mean Squared Displacement - %s'\
                    % (key_title)
                gp.c('set title "%s"' % (g_title))
                tau = Analysis.TauCalc(self.bacteria.config[key])
                gp.c('set xrange [%f:%f]' % (tau.min()*0.75, tau.max()*1.25))
                results_array = parallel(delayed(
                    Analysis.Linear)(self.bacteria.bacterium[key][bact],
                                     self.bacteria.config[key])
                    for bact in self.bacteria.bacterium[key].keys())
                size = len(results_array)
                dat_name = os.path.join(self.plot_dir,
                                        '%s_msd_lin.dat' % (key))
                graph_out = np.vstack((tau, results_array))
                gp.s(graph_out, dat_name)
                title = ['notitle' for i in range(size)]
                plot_string = plotStringSingleFile(size, dat_name,
                                                   'with points', title)
                gp.c(plot_string)
                output = os.path.join(self.graph_dir,
                                      '%s_linear_mean.png' % (key))
                gp.c('set output "%s"' % (output))
                mean_results = np.mean(results_array, axis=0)
                std_dev = np.std(results_array, axis=0)
                std_error = std_dev/np.sqrt(size)
                current_results = np.vstack(
                    (tau, mean_results, std_error))
                dat_name = os.path.join(self.plot_dir,
                                        '%s_msd_lin_mean.dat' % (key))
                gp.s(current_results, dat_name)
                plot_string = 'plot "%s" u 1:2:3 with yerrorbars' % (dat_name)
                plot_string = plot_string + ' title "Mean Linear MSD"'
                gp.c(plot_string)
                amalg_dat_name.append(dat_name)
                amalg_titles.append('title "%s"' % (key_title))
                print('Completed %s \t Linear Analysis' % (key))
            amalg_formatting = 'u 1:2:3 with yerrorlines'
            amalg_plot_string = plotStringMultiFile(len(amalg_dat_name),
                                                    amalg_dat_name,
                                                    amalg_formatting,
                                                    amalg_titles)
            output = os.path.join(self.graph_dir, 'linear_mean_amalg.png')
            gp.c('set output "%s"' % (output))
            g_title = 'Analysis of Linear Mean Squared Displacement'
            gp.c('set title "%s"' % (g_title))
            gp.c('set xrange [*:*]')
            gp.c(amalg_plot_string)

# %% Linear - High Range (>1 sec)
            gp.c('reset')
            gp.c('set xlabel "{/Symbol t} (s)"')
            gp.c('set ylabel "MSD (m^2)"')
            gp.c('set key top left')
            gp.c("set terminal pngcairo enhanced"
                 + " size 1600,1200 font 'ariel, 14'")
            amalg_dat_name = []
            amalg_titles = []
            amalg_grad = []
            amalg_grad_titles = []
            for key in self.bacteria.bacterium.keys():
                line_colour = 1
                key_title = self.bacteria.config[key].name
                print('Started: %s \t Linear Analysis High Range'
                      % (key_title))
                output = os.path.join(self.graph_dir,
                                      '%s_linear_hr.png' % (key))
                gp.c('set output "%s"' % (output))
                g_title = 'Analysis of Linear Mean Squared Displacement %s'\
                    % (key_title)
                gp.c('set title "%s"' % (g_title))
                tau = Analysis.TauCalcHR(self.bacteria.config[key])
                gp.c('set xrange [%f:%f]' % (tau.min()-5, tau.max()+5))
                results_array = parallel(delayed(
                    Analysis.LinearHighRange)
                    (self.bacteria.bacterium[key][bact],
                     self.bacteria.config[key])
                    for bact in self.bacteria.bacterium[key].keys())
                size = len(results_array)
                dat_name = os.path.join(self.plot_dir,
                                        '%s_msd_lin_hr.dat' % (key))
                graph_out = np.vstack((tau, results_array))
                gp.s(graph_out, dat_name)
                title = ['notitle' for i in range(size)]
                plot_string = plotStringSingleFile(size, dat_name,
                                                   'with points', title)
                gp.c(plot_string)
                output = os.path.join(self.graph_dir,
                                      '%s_linear_mean_hr.png' % (key))
                gp.c('set output "%s"' % (output))
                mean_results = np.mean(results_array, axis=0)
                std_dev = np.std(results_array, axis=0)
                std_error = std_dev/np.sqrt(size)
                current_results = np.vstack(
                    (tau, mean_results, std_error))
                gradient, y_intercept, r_value, p_value, grad_err\
                    = linregress(tau, mean_results)
                exp_diff = "Gradient = %.5e {/Symbol \261} %.5e" % (gradient,
                                                                    grad_err)
                r_2 = "R^2 = %f" % (r_value**2)
                fit_title = ("%s, %s, %s") % (key_title, exp_diff, r_2)
                dat_name = os.path.join(self.plot_dir,
                                        '%s_msd_lin_mean_hr.dat' % (key))
                gp.s(current_results, dat_name)
                plot_string = 'plot "%s" u 1:2:3 with yerrorbars lc %d' %\
                    (dat_name, line_colour)
                plot_string = plot_string + ' title "%s - Mean MSD"'\
                    % (key_title)
                plot_string = plot_string + ', %e*x lc %d' %\
                    (gradient, line_colour)
                plot_string = plot_string + 'title "%s"' % (fit_title)
                gp.c(plot_string)
                amalg_dat_name.append(dat_name)
                amalg_titles.append('title "%s - Mean MSD" ' % (key_title))
                amalg_grad.append(gradient)
                amalg_grad_titles.append(fit_title)
                print('Completed %s \t Linear Analysis High Range'
                      % (key_title))
            amalg_formatting = 'u 1:2:3 with yerrorbars'
            amalg_plot_string = plotStringMultiFileWithFit(len(amalg_dat_name),
                                                    amalg_dat_name,
                                                    amalg_formatting,
                                                    amalg_titles,
                                                    amalg_grad,
                                                    amalg_grad_titles)
            output = os.path.join(self.graph_dir, 'linear_mean_amalg_hr.png')
            gp.c('set output "%s"' % (output))
            g_title = 'Analysis of Linear Mean Squared Displacement'
            gp.c('set title "%s"' % (g_title))
            gp.c('set xrange [*:*]')
            gp.c(amalg_plot_string)

# %% Rotational Analysis

            amalg_dat_name = []
            amalg_titles = []
            gp.c('reset')
            gp.c('set logscale xy 10')
            gp.c('set xlabel "{/Symbol t} (s)"')
            gp.c('set ylabel "MSD ({/Symbol q}^2)"')
            gp.c('set key top left')
            gp.c("set terminal pngcairo enhanced"
                 + " size 1600,1200 font 'ariel, 14'")
            for key in self.bacteria.bacterium.keys():
                key_title = self.bacteria.config[key].name
                print("Started %s \t Rotational Analysis" % (key))
                output = os.path.join(self.graph_dir,
                                      '%s_rotational.png' % (key))
                gp.c('set output "%s"' % (output))
                g_title = 'Analysis of Rotational Mean Squared '\
                    + 'Displacement - %s' % (key)
                gp.c('set title "%s" noenhanced' % (g_title))
                tau = Analysis.TauCalc(self.bacteria.config[key])
                gp.c('set xrange [%f:%f]' % (tau.min()*0.75, tau.max()*1.25))
                results_array = parallel(delayed(
                    Analysis.Rotational)(self.bacteria.bacterium[key][bact],
                                         self.bacteria.config[key])
                    for bact in self.bacteria.bacterium[key].keys())
                size = len(results_array)
                dat_name = os.path.join(self.plot_dir,
                                        '%s_msd_rot.dat' % (key))
                graph_out = np.vstack((tau, results_array))
                gp.s(graph_out, dat_name)
                title = ['notitle' for i in range(size)]
                plot_string = plotStringSingleFile(size, dat_name,
                                                   'with points', title)
                gp.c(plot_string)
                output = os.path.join(self.graph_dir,
                                      '%s_rotational_mean.png' % (key))
                gp.c('set output "%s"' % (output))
                mean_results = np.mean(results_array, axis=0)
                std_dev = np.std(results_array, axis=0)
                std_error = std_dev/np.sqrt(size)
                current_results = np.vstack(
                    (tau, mean_results, std_error))
                dat_name = os.path.join(self.plot_dir,
                                        '%s_msd_rot_mean.dat' % (key))
                gp.s(current_results, dat_name)
                plot_string = 'plot "%s" u 1:2:3 with yerrorbars' % (dat_name)
                plot_string = plot_string + ' title "Mean Rotational MSD"'
                gp.c(plot_string)
                amalg_dat_name.append(dat_name)
                amalg_titles.append('title "%s"' % (key_title))
                print("Completed %s \t Rotational Analysis" % (key))
            amalg_formatting = 'u 1:2:3 with yerrorlines'
            amalg_plot_string = plotStringMultiFile(len(amalg_dat_name),
                                                    amalg_dat_name,
                                                    amalg_formatting,
                                                    amalg_titles)
            output = os.path.join(self.graph_dir, 'rotational_mean_amalg.png')
            gp.c('set output "%s"' % (output))
            g_title = 'Analysis of Rotational Mean Squared Displacement'
            gp.c('set title "%s"' % (g_title))
            gp.c('set xrange [*:*]')
            gp.c(amalg_plot_string)

# %%

            gp.c('reset')
            gp.c('set key top left')
            gp.c("set terminal pngcairo enhanced"
                 + " size 1600,1200 font 'ariel, 14'")
            gp.c('unset logscale')
            gp.c('set ylabel "Probability Density"')
            gp.c('set xlabel "Run to Run Angle (degrees)"')
            amalg_dat_name = []
            amalg_titles = []
            for key in self.bacteria.bacterium.keys():
                key_title = self.bacteria.config[key].name
                print("Started %s \t Run to Run angles" % (key))
                if not self.bacteria.config[key].run_behaviour:
                    print("%s is non-motile, ignoring" % (key))
                    continue
                if self.bacteria.config[key].archaea_mode:
                    print("%s  is an archaea, ignoring" % (key))
                    continue
                output = os.path.join(self.graph_dir,
                                      '%s_run_run_angle.png' % (key))
                gp.c('set output "%s"' % (output))
                title = 'Analysis of Run to Run Angle - %s'\
                    % (key)
                gp.c('set title "%s"' % (title))
                angle_list = parallel(delayed(Analysis.RunRunAngles)
                                      (self.bacteria.cosines[key][bact])
                                      for bact in
                                      self.bacteria.cosines[key].keys())
                angle_array = []
                for i in range(len(angle_list)):
                    angle_array = np.append(angle_array, angle_list[i])
                angle_bins = np.linspace(0, np.pi, 40)
                angle_mean = np.mean(angle_array)
                angle_std = np.std(angle_array)
                angle_std_err = angle_std/np.sqrt(len(angle_array))
                self.LDValues[key].avg_tumble = angle_mean
                self.LDValues[key].tumble_err = angle_std_err
                angle_med = np.median(angle_array)
                results, bin_edges = np.histogram(angle_array,
                                                  bins=angle_bins,
                                                  density=True)
                angle_points = np.delete(angle_bins, -1) + np.diff(angle_bins)/2
                graph_out = np.vstack((angle_points, results))
                title = "%s, Mean = %6.2f, std. dev. = %6.2f, Median = %6.2f"\
                    % (key_title, angle_mean, angle_std, angle_med)
                dat_name = os.path.join(self.plot_dir,
                                        '%s_run_hist.dat' % (key))
                gp.s(graph_out, dat_name)
                plot_string = 'plot "%s" u 1:2 with points title "%s"'\
                    % (dat_name, title)
                gp.c(plot_string)
                amalg_dat_name.append(dat_name)
                amalg_titles.append('title "%s"' % (title))
                print("Completed %s \t Run to Run angles" % (key))
            amalg_formatting = 'u 1:2 with points'
            if amalg_dat_name:
                amalg_plot_string = plotStringMultiFile(len(amalg_dat_name),
                                                        amalg_dat_name,
                                                        amalg_formatting,
                                                        amalg_titles)
                output = os.path.join(self.graph_dir,
                                      'run_run_angle_amalg.png')
                gp.c('set output "%s"' % (output))
                g_title = 'Analysis of Run to Run Angles'
                gp.c('set title "%s"' % (g_title))
                gp.c('set xrange [*:*]')
                gp.c(amalg_plot_string)

# %%
            gp.c('reset')
            gp.c('set key top left')
            gp.c("set terminal pngcairo enhanced"
                 + " size 1600,1200 font 'ariel, 14'")
            gp.c('set logscale y')
            gp.c('set ylabel "Probability Density"')
            gp.c('set xlabel "Run Duration (s)"')
            gp.c('set xrange [*:*]')
            amalg_dat_name = []
            amalg_titles = []
            for key in self.bacteria.bacterium.keys():
                key_title = self.bacteria.config[key].name
                print("Started %s \t Run durations" % (key))
                if not self.bacteria.config[key].run_behaviour:
                    print("%s is non-motile, ignoring" % (key))
                    continue

                output = os.path.join(self.graph_dir,
                                      '%s_run_duration.png' % (key))
                gp.c('set output "%s"' % (output))
                title = 'Analysis of Run duration - %s'\
                    % (key)
                gp.c('set title "%s"' % (title))
                time_list = parallel(delayed(Analysis.GetTimes)
                                     (self.bacteria.run_log[key][bact],
                                      self.bacteria.config[key])
                                     for bact in
                                     self.bacteria.run_log[key].keys())
                time_array = []
                for i in range(len(time_list)):
                    time_array = np.append(time_array, time_list[i])

                time_mean = np.mean(time_array)
                time_std = np.std(time_array)
                time_std_err = time_std/(np.sqrt(len(time_array)))
                self.LDValues[key].avg_run_duration = time_mean
                self.LDValues[key].run_dur_err = time_std_err

                time_med = np.median(time_array)
                results, bin_edges = np.histogram(time_array,
                                                  bins='auto',
                                                  density=True)
                time_points = np.delete(bin_edges + np.mean(
                    np.diff(bin_edges))/2, -1)
                graph_out = np.vstack((time_points, results))
                title = "%s, Mean = %6.2f, std. dev. = %6.2f, Median = %6.2f"\
                    % (key_title, time_mean, time_std, time_med)
                dat_name = os.path.join(self.plot_dir,
                                        '%s_runduration_hist.dat' % (key))
                gp.s(graph_out, dat_name)
                plot_string = 'plot "%s" u 1:2 with points title "%s"'\
                    % (dat_name, title)
                gp.c(plot_string)
                amalg_dat_name.append(dat_name)
                amalg_titles.append('title "%s"' % (title))
                print("Completed %s \t Run duration" % (key))
            if amalg_dat_name:
                amalg_formatting = 'u 1:2 with points'
                amalg_plot_string = plotStringMultiFile(len(amalg_dat_name),
                                                        amalg_dat_name,
                                                        amalg_formatting,
                                                        amalg_titles)
                output = os.path.join(self.graph_dir, 'run_duration_amalg.png')
                gp.c('set output "%s"' % (output))
                g_title = 'Analysis of Run duration'
                gp.c('set title "%s"' % (g_title))
                gp.c('set xrange [*:*]')
                gp.c(amalg_plot_string)

# %%

            gp.c('reset')
            gp.c('set key top left')
            gp.c("set terminal pngcairo enhanced"
                 + " size 1600,1200 font 'ariel, 14'")
            gp.c('set logscale y')
            gp.c('set ylabel "Probability Density"')
            gp.c('set xlabel "Tumble Duration (s)"')
            gp.c('set xrange [*:*]')
            amalg_dat_name = []
            amalg_titles = []
            for key in self.bacteria.bacterium.keys():
                key_title = self.bacteria.config[key].name
                print("Started %s \t Tumble durations" % (key))
                if not self.bacteria.config[key].run_behaviour:
                    print("%s is non-motile, ignoring" % (key))
                    continue
                if self.bacteria.config[key].archaea_mode:
                    print("%s  is an archaea, ignoring" % (key))
                    continue

                output = os.path.join(self.graph_dir,
                                      '%s_tumble_duration.png' % (key))
                gp.c('set output "%s"' % (output))
                title = 'Analysis of Tumble duration - %s'\
                    % (key_title)
                gp.c('set title "%s"' % (title))
                time_list = parallel(delayed(Analysis.GetTimes)
                                     (self.bacteria.tumble_log[key][bact],
                                      self.bacteria.config[key])
                                     for bact in
                                     self.bacteria.run_log[key].keys())
                time_array = []
                for i in range(len(time_list)):
                    time_array = np.append(time_array, time_list[i])

                time_mean = np.mean(time_array)
                self.LDValues[key].avg_tumble_duration = time_mean
                time_std = np.std(time_array)
                time_med = np.median(time_array)
                results, bin_edges = np.histogram(time_array,
                                                  bins='auto',
                                                  density=True)
                time_points = np.delete(bin_edges+np.mean(
                    np.diff(bin_edges))/2, -1)
                graph_out = np.vstack((time_points, results))
                title = "%s, Mean = %6.2f, std. dev. = %6.2f, Median = %6.2f"\
                    % (key_title, time_mean, time_std, time_med)
                dat_name = os.path.join(self.plot_dir,
                                        '%s_tumbleduration_hist.dat' % (key))
                gp.s(graph_out, dat_name)
                plot_string = 'plot "%s" u 1:2 with points title "%s"'\
                    % (dat_name, title)
                gp.c(plot_string)
                amalg_dat_name.append(dat_name)
                amalg_titles.append('title "%s"' % (title))
                print("Completed %s \t Tumble duration" % (key))
            amalg_formatting = 'u 1:2 with points'
            if amalg_dat_name:
                amalg_plot_string = plotStringMultiFile(len(amalg_dat_name),
                                                        amalg_dat_name,
                                                        amalg_formatting,
                                                        amalg_titles)
                output = os.path.join(self.graph_dir,
                                      'tumble_duration_amalg.png')
                gp.c('set output "%s"' % (output))
                g_title = 'Analysis of Tumble duration'
                gp.c('set title "%s"' % (g_title))
                gp.c('set xrange [*:*]')
                gp.c(amalg_plot_string)
            LD_file = os.path.join(self.plot_dir,"LD_values.txt")
            with open(LD_file, "w") as LD_f:
                for key in self.bacteria.bacterium.keys():
                    if self.bacteria.config[key].run_behaviour:
                        self.LDValues[key].LDCalc()
                        write_string = "%s \t Name: %s \tLD Value: %e\n"\
                                       %    (key, self.bacteria.config[key].name,
                                            self.LDValues[key].LD_Diff)
                        LD_f.write(write_string)

