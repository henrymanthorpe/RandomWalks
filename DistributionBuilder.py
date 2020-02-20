#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 20:29:39 2020

@author: henry
"""

import numpy as np
from scipy import optimize
import PyGnuplot as gp

sqrt_2pi = np.sqrt(2*np.pi)

def LogNormal(x, mu, sigma):
    return (1/x)*(1/(sigma*sqrt_2pi))*np.exp(-(np.log(x-mu)**2)/(2*sigma**2))

class Build:
    def __init__(self,fname):
        self.distribution =  np.swapaxes(np.loadtxt(fname,delimiter=','),0,1)
        self.distribution[0] = self.distribution[0]/180
        self.distribution[1] = self.distribution[1]/np.sum(self.distribution[1])
        self.params, self.param_convergence = optimize.curve_fit(LogNormal, self.distribution[0], self.distribution[1], p0=(0,1), bounds=(0,np.inf))


def GraphTest(build):
    gp.c('reset')
    gp.c('set terminal qt 0')
    gp.s(build.distribution)
    gp.c('a = 0')
    gp.c('b = 1')
    gp.c('c = '+str(sqrt_2pi))
    gp.c('f(x) = (1/(x*b*c))*exp(-((log(x-a)**2)/(2*b**2)))')
    gp.c('plot f(x)')
    