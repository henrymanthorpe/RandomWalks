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
    y = tumble_dist[1]
    p = np.poly1d(np.polyfit(x, y, poly))
    if graph is True:
        t = np.linspace(0, np.pi, 400)
        plt.plot(x, y, 'o', t, p(t), '-')
        plt.show()
        print(np.poly1d(p))
    return p

def ManualFit():
    tumble_dist = np.swapaxes(np.loadtxt
                              ("tumble_dist.csv", delimiter=','), 0, 1)
    x = np.deg2rad(tumble_dist[0])
    print(len(x))
    y = tumble_dist[1]
    hist_data = np.full(int(y[0]),x[0])
    for i in range(1,len(x)):
        np.hstack((hist_data, np.full(int(y[i]),x[i])))
    return hist_data
    # plt.hist(hist_data,bins='auto',density=True)
    # plt.show()
