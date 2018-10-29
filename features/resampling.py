#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 09:46:44 2018

@author: sm7gc
"""

# Imports
import numpy as np
import pandas as pd
from scipy import signal
import warnings

warnings.filterwarnings(action='once')

def resample(feat_df,total_start,total_end,target_hz):
    # Device ID -> Device Name Dict for 6/14/18 Experiment
    device_dict = {"60bfd1a1721a5e02": "Pixel2-walleye",
                   "09f392ab779b98fc":"Pixel2-taimen",
                   "39CFD493-D958-4726-AC01-02596ADB5998":"iPhone9.1",
                   "6DD4FF11-386A-4092-B849-F8C3D1E4D6C5":"iPhone10.1"}
    
#    total_start = datetime.strptime('6/14/2018 16:03:00',  "%m/%d/%Y %H:%M:%S")
#    total_end = datetime.strptime('6/14/2018  17:38:54',  "%m/%d/%Y %H:%M:%S")
    
    # Calculate actual sampling frequency
    freq = {}
    sep = 'DeviceId'
    sep_col = feat_df[sep].unique()
    
    # Plotting actual sampling freq (Hz) per device
    
    time_window = 10
    
    # Separate by DeviceId
    for c in sep_col:
        if c in device_dict:
            
            # Get data for specific device and select data from collection datetime range
            device_df = feat_df[feat_df[sep] == c]
            device_df = device_df[device_df.index >= total_start]
            device_df = device_df[device_df.index <= total_end] 
    
            # Resample data on 10 second interval
            resampled = device_df.groupby(pd.Grouper(freq=str(time_window)+'s'))
    
#            actual_hz = int(resampled['X'].count().mean())
#            print(len(device_df.index)/actual_hz) # Number of time_window samples before resampling
    
            timestamp, x, y, z, pid, activity, position = [],[],[],[],[],[],[]
            
            # Iterate through resampled data
            for index, row in resampled:
                if (len(row) == 0): continue
            
                start = pd.Timestamp(row.index[0])
                end = pd.Timestamp(row.index[len(row)-1])
                rs_timestamp = pd.to_datetime(np.linspace(start.value, end.value, target_hz*time_window))
                
                rs_x = signal.resample(row['X'].values,target_hz*time_window)
                rs_y = signal.resample(row['Y'].values,target_hz*time_window)
                rs_z = signal.resample(row['Z'].values,target_hz*time_window)
                
                mode_pid = max(set(list(row['PID'])), key=list(row['PID']).count)
                mode_activity = max(set(list(row['Activity'])), key=list(row['Activity']).count)
                mode_position = max(set(list(row['Device Position'])), key=list(row['Device Position']).count)
                
                rs_pid = [mode_pid] *len(rs_x)
                rs_activity = [mode_activity] *len(rs_x)
                rs_position = [mode_position] *len(rs_x)
                
                timestamp.extend(rs_timestamp)
                x.extend(rs_x)
                y.extend(rs_y)
                z.extend(rs_z)
                               
                pid.extend(rs_pid)
                activity.extend(rs_activity)
                position.extend(rs_position)
    
            rs_df = pd.DataFrame({'Timestamp': timestamp,'X': x,'Y': y,'Z': z,'PID':pid,'Activity':activity,'Device Position':position})
            rs_df = rs_df.set_index(['Timestamp'])
            
            # print(rs_df.groupby(pd.Grouper(freq='1s')).count().mode()) # verify sampling freq
    
            # Store sampling frequency measure in freq
            device = device_dict[c]
            freq[device] = rs_df
#            print(len(freq[device])/(target_hz*time_window)) # Number of time_window samples after resampling
    
    freq_keys = list(device_dict.values())
    
    return freq, freq_keys

