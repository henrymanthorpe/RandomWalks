#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 14:29:58 2020

@author: henry
"""


import numpy as np
import matplotlib.pyplot as plt


def Fit(poly, graph=False):
    tumble_dist = np.swapaxes(np.loadtxt
                              ("tumble_dist.csv", delimiter=','), 0, 1)
    x = np.deg2rad(tumble_dist[0])
    y = np.cumsum(tumble_dist[1])/np.sum(tumble_dist[1])
    p = np.poly1d(np.polyfit(x, y, poly))
    if graph is True:
        t = np.linspace(0, np.pi, 400)
        plt.plot(x, y, 'o', t, p(t), '-')
        plt.show()
        print(np.poly1d(p))
    return p
