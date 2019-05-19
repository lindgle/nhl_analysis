# -*- coding: utf-8 -*-
"""
Created on Sun May 12 20:37:49 2019
Helper functions for NHL stuff

@author: Leevi
"""
import numpy as np

def prev_season_ability(x):
    '''
    Computes previous season ability
    Input:
    -----
    x - vector of points
    '''
    
    x_max = np.max(x)
    x_min = np.min(x)
    
    res = 2*x/(x_max - x_min) - (x_max + x_min)/((x_max - x_min))
    
    return res