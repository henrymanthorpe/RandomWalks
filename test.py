#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 15:42:19 2020

@author: henry
"""

import numpy as np
import PyGnuplot as gp

def Test(n):
    out = np.random.exponential(1.0, n)
    out = out/out.max()
    out2 = np.random.normal(out,1,n)
    out2 = out2/out2.max()
    return out2