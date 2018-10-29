#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 09:46:44 2018

@author: sm7gc
"""

import numpy as np
from astropy.stats import median_absolute_deviation
from scipy.stats import pearsonr
from scipy.stats import entropy
from scipy.stats import skew
from scipy.stats import kurtosis


def mag_acc(x, y, z):
    mpre = x*x+y*y+z*z
    m = np.sqrt(mpre)
    m_smooth = m
    m_smooth[2:(len(m_smooth)-2)] = [(m[i-2] + m[i-1] +m[i] + m[i+1] + m[i+2])/5 for i ,val in enumerate(m[2:(len(m)-2)])]
    return m_smooth

#def stft(x, window_size, overlap=2):
#    hop = int(window_size / overlap)
#    w = scipy.hanning(window_size+1)[:-1]
#    return [np.fft.rfft(w*x[i:i+window_size]) for i in range(0, len(x)-window_size, hop)] 

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
    x_feat = [entropy(i) for i in x]
    y_feat = [entropy(i) for i in y]
    z_feat = [entropy(i) for i in z]
    m_feat = [entropy(i) for i in m]
    return x_feat, y_feat, z_feat, m_feat

#def fft_acc(x, y, z, window_size, overlap=2):
#    fftx = np.fft.fft(x)
#    timestep = 0.1
#    freq = np.fft.fftfreq(len(x), d=timestep)   
#    return fftx
    

## Accelerometer Featurization: https://github.com/yatharthsharma/Activity-Recognition/blob/master/featues.py
#def triaxial_feat(x,y,z):
#    
#    energy_signal = [np.sum(np.power(abs(stft_signal[i]),2)) for i in range(len(stft_signal))]
#    plt.plot(energy_signal)
#    plt.show()
#    #SMA + Signal magnitude vector
#    smasum = 0
#    smvsum = 0
#    for i in range(len(x)):
#         smasum += (abs(x[i]) + abs(y[i]) + abs(z[i]))
#         smvsum += x[i]**2 + y[i]**2 + z[i]**2;
#    sma=smasum / len(x)
#    smv= np.sqrt(smvsum)/len(x)
#    
#    absolute_start_time = time.time()
#    
#    print("Total Program Runtime: " + str(time.time() - absolute_start_time))
#    
#    valmean, valmax, valmin, valstd, valenergy = feature(m,120)
#    diff = np.subtract(valmax,valmin)
#
#
#    return [valmean, valmax, valmin, valstd, valenergy, diff, sma,smv]
