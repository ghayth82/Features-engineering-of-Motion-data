#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 09:46:44 2018

@author: mob3f
"""

# Imports
import numpy as np
import pandas as pd
from scipy import signal


def invalidTimestamp(datetime,datetime_range):
    for dt in datetime_range:
        start = datetime.strptime(dt[0],  "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(dt[1],  "%Y-%m-%d %H:%M:%S")
        if datetime >= start and datetime <= end:
            return False
    return True

def resample(feat_df,target_hz,sep,datetime_range):

    # Calculate actual sampling frequency
    freq = {}
    sep_col = feat_df[sep].unique()
    if sep == 'Device ID':
        device_dict = dict(zip(list(feat_df['Device ID']), list(feat_df['Device Model'])))
        sep_col = [c for c in sep_col if c in device_dict]

    time_window = 10
    
    # Separate by DeviceId
    for c in sep_col:
        if sep == 'Device ID': print("----- "+device_dict[c])
        else: print("----- "+c)
        
        # Get data for specific device and select data from collection datetime range
        device_df = feat_df[feat_df[sep] == c]

        # Resample data on 10 second interval
        resampled = device_df.groupby(pd.Grouper(freq=str(time_window)+'s'))

        timestamp, x, y, z, pid, activity, position, devid = [],[],[],[],[],[],[],[]

        # Iterate through resampled data
        for index, row in resampled:
            if invalidTimestamp(index,datetime_range): continue
        
            dt = pd.date_range(start=index, periods=2, freq='10S')
            start = dt[0]
            end = dt[1]
            rs_timestamp = pd.to_datetime(np.linspace(start.value, end.value, target_hz*time_window))
                
            if (len(row) == 0): 
                rs_x, rs_y, rs_z = np.zeros(target_hz*time_window), np.zeros(target_hz*time_window), np.zeros(target_hz*time_window)
                rs_pid, rs_activity, rs_position, rs_devid = np.repeat('Unknown',target_hz*time_window), np.repeat('Unknown',target_hz*time_window), np.repeat('Unknown',target_hz*time_window), np.repeat('Unknown',target_hz*time_window)
            else:
                
                rs_x = signal.resample(row['X'].values,target_hz*time_window)
                rs_y = signal.resample(row['Y'].values,target_hz*time_window)
                rs_z = signal.resample(row['Z'].values,target_hz*time_window)
            
                rs_pid, rs_activity, rs_position, rs_devid = [], [], [], []
                for t in rs_timestamp:
                    min_ind = np.argmin(np.abs(row.index - t))
                    rs_pid.append(row['PID'][min_ind])
                    rs_activity.append(row['Activity'][min_ind])
                    rs_position.append(row['Device Position'][min_ind])
                    rs_devid.append(row['Device ID'][min_ind])
                
            timestamp.extend(rs_timestamp)
            x.extend(rs_x)
            y.extend(rs_y)
            z.extend(rs_z)
                           
            pid.extend(rs_pid)
            activity.extend(rs_activity)
            position.extend(rs_position)
            devid.extend(rs_devid)

        rs_df = pd.DataFrame({'Timestamp': timestamp,'X': x,'Y': y,'Z': z,'PID':pid,'Activity':activity,'Device Position':position,'DeviceId':devid})
        print(len(rs_df))
        rs_df = rs_df.set_index(['Timestamp'])

        if sep == 'Device ID': key = device_dict[c]
        elif sep == "Sensus OS": key = c.replace(" Sensus","")
        else: key = c
        freq[key] = rs_df
    
    return freq, list(freq.keys())