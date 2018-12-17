#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 09:46:44 2018

@author: mob3f
"""

import numpy as np
from astropy.stats import median_absolute_deviation
from scipy.stats import pearsonr
from scipy.stats import skew
from scipy.stats import kurtosis
from librosa.feature import mfcc
from pyentrp import entropy as ent


# =============================================================================
# Accelerometer (Tri-Axial) Features
# =============================================================================

def mag_acc(x, y, z):
    mpre = x*x+y*y+z*z
    m = np.sqrt(mpre)
    m_smooth = m
#    m_smooth[2:(len(m_smooth)-2)] = [(m[i-2] + m[i-1] +m[i] + m[i+1] + m[i+2])/5 for i ,val in enumerate(m[2:(len(m)-2)])]
    return m_smooth

def mean_acc(x, y, z, m):
    x_feat = [np.mean(i) for i in x]
    y_feat = [np.mean(i) for i in y]
    z_feat = [np.mean(i) for i in z]
    m_feat = [np.mean(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def max_acc(x, y, z, m):
    x_feat = [np.max(i) for i in x]
    y_feat = [np.max(i) for i in y]
    z_feat = [np.max(i) for i in z]
    m_feat = [np.max(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def min_acc(x, y, z, m):
    x_feat = [np.min(i) for i in x]
    y_feat = [np.min(i) for i in y]
    z_feat = [np.min(i) for i in z]
    m_feat = [np.min(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def median_acc(x, y, z, m):
    x_feat = [np.median(i) for i in x]
    y_feat = [np.median(i) for i in y]
    z_feat = [np.median(i) for i in z]
    m_feat = [np.median(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def std_acc(x, y, z, m):
    x_feat = [np.std(i) for i in x]
    y_feat = [np.std(i) for i in y]
    z_feat = [np.std(i) for i in z]
    m_feat = [np.std(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def energy_acc(x, y, z, m):
    x_feat = [np.sum(np.power(i,2)) for i in x]
    y_feat = [np.sum(np.power(i,2)) for i in y]
    z_feat = [np.sum(np.power(i,2)) for i in z]
    m_feat = [np.sum(np.power(i,2)) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def mad_acc(x, y, z, m):
    #mad= np.mean(np.absolute(x - np.mean(x))) # Mean Absolute Deviation formula
    x_feat = [median_absolute_deviation(i) for i in x]
    y_feat = [median_absolute_deviation(i) for i in y]
    z_feat = [median_absolute_deviation(i) for i in z]
    m_feat = [median_absolute_deviation(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def perc_acc(x, y, z, m, percent):
    x_feat = [np.percentile(i,percent) for i in x]
    y_feat = [np.percentile(i,percent) for i in y]
    z_feat = [np.percentile(i,percent) for i in z]
    m_feat = [np.percentile(i,percent) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def iqr_acc(x, y, z, m):
    x_feat = [np.percentile(i,75)-np.percentile(i,25) for i in x]
    y_feat = [np.percentile(i,75)-np.percentile(i,25) for i in y]
    z_feat = [np.percentile(i,75)-np.percentile(i,25) for i in z]
    m_feat = [np.percentile(i,75)-np.percentile(i,25) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def ptop_acc(x, y, z, m):
    x_feat = [np.max(i)-np.min(i) for i in x]
    y_feat = [np.max(i)-np.min(i) for i in y]
    z_feat = [np.max(i)-np.min(i) for i in z]
    m_feat = [np.max(i)-np.min(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def zcr_acc(x, y, z, m):
    x_feat = [(np.diff(np.sign(i))!= 0).sum() for i in x]
    y_feat = [(np.diff(np.sign(i))!= 0).sum() for i in y]
    z_feat = [(np.diff(np.sign(i))!= 0).sum() for i in z]
    m_feat = [(np.diff(np.sign(i))!= 0).sum() for i in m]
    return x_feat, y_feat, z_feat, m_feat

def mcr_acc(x, y, z, m):
    x_feat = [(np.diff(np.sign(i-np.mean(i)))!= 0).sum() for i in x]
    y_feat = [(np.diff(np.sign(i-np.mean(i)))!= 0).sum() for i in y]
    z_feat = [(np.diff(np.sign(i-np.mean(i)))!= 0).sum() for i in z]
    m_feat = [(np.diff(np.sign(i-np.mean(i)))!= 0).sum() for i in m]
    return x_feat, y_feat, z_feat, m_feat

def minind_acc(x, y, z, m):
    x_feat = [i.index.get_loc(i.idxmin()) for i in x]
    y_feat = [i.index.get_loc(i.idxmin()) for i in y]
    z_feat = [i.index.get_loc(i.idxmin()) for i in z]
    m_feat = [i.index.get_loc(i.idxmin()) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def maxind_acc(x, y, z, m):
    x_feat = [i.index.get_loc(i.idxmax()) for i in x]
    y_feat = [i.index.get_loc(i.idxmax()) for i in y]
    z_feat = [i.index.get_loc(i.idxmax()) for i in z]
    m_feat = [i.index.get_loc(i.idxmax()) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def sma_acc(x, y, z):
    sma = [sum(abs(x[i])+abs(y[i])+abs(z[i])) for i in range(len(x))]
    return sma

def svm_acc(x, y, z):
    svm = [sum(x[i]**2 + y[i]**2 + z[i]**2) for i in range(len(x))]
    return svm

def kurt_acc(x, y, z, m):
    x_feat = [kurtosis(i) for i in x]
    y_feat = [kurtosis(i) for i in y]
    z_feat = [kurtosis(i) for i in z]
    m_feat = [kurtosis(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def skew_acc(x, y, z, m):
    x_feat = [skew(i) for i in x]
    y_feat = [skew(i) for i in y]
    z_feat = [skew(i) for i in z]
    m_feat = [skew(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def cor_acc(x, y, z):
    xy_feat = [pearsonr(x[i],y[i])[0] for i in range(len(x))]
    yz_feat = [pearsonr(y[i],z[i])[0] for i in range(len(y))]
    xz_feat = [pearsonr(x[i],z[i])[0] for i in range(len(z))]
    return xy_feat, yz_feat, xz_feat

def entropy_acc(x, y, z, m):
    x_feat = [ent.permutation_entropy(list(i)) for i in x]
    y_feat = [ent.permutation_entropy(list(i)) for i in y]
    z_feat = [ent.permutation_entropy(list(i)) for i in z]
    m_feat = [ent.permutation_entropy(list(i)) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def mfcc_acc(x, y, z, m):
    x_feat = [mfcc(i.values) for i in x]
    y_feat = [mfcc(i.values) for i in y]
    z_feat = [mfcc(i.values) for i in z]
    m_feat = [mfcc(i.values) for i in m]
    return x_feat, y_feat, z_feat, m_feat

def fft_acc(x, y, z, m):
    x_feat = [np.fft.fft(i) for i in x]
    y_feat = [np.fft.fft(i) for i in y]
    z_feat = [np.fft.fft(i) for i in z]
    m_feat = [np.fft.fft(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat
