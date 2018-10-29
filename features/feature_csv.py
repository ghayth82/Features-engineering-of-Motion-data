#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 09:37:55 2018

@author: sm7gc
"""

#import os
#data_folder = './../../Controlled' # Laptop filepath
#data_folder = './../../Labeled/06-14-18/Controlled' # Lab Comp
#filenames = [os.path.join(dp, f) for dp, dn, filenames in os.walk(data_folder) for f in filenames if os.path.splitext(f)[1] == '.csv']
#filenames = ['./../Controlled/Accelerometer.csv','./../Controlled/Compass.csv','./../Controlled/Smartwatch_LinearAcceleration.csv']

import time
import pandas as pd
from datetime import datetime
from dateutil import tz
import warnings
import feature_extraction as fe
import resampling as re

warnings.filterwarnings("ignore")

# Format timestamp and convert from GMT to EST for comparison purposes (Helper)
def formatTimestamp(timestamp):

    timestamp = timestamp.split('+')[0]
    if len(timestamp.split('.')) == 1:
        timestamp = timestamp + '.0000'
    timestamp = datetime.strptime(timestamp,  "%Y-%m-%dT%H:%M:%S.%f")

    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')

    timestamp = timestamp.replace(tzinfo=from_zone)

    timestamp = timestamp.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S.%f')
    return datetime.strptime(timestamp,  "%Y-%m-%d %H:%M:%S.%f")


absolute_start_time = time.time() # Program Start Time

filenames = ['/Users/sm7gc/Desktop/WASH/Labeled/06-14-18/Controlled/Accelerometer.csv']
target_path = '/Users/sm7gc/Desktop/WASH/Featurized'

# Read Raw Accelerometer Data
for i in range(len(filenames)):
    filename = filenames[i]
    
    start_time = time.time()
    print("File " + str(i+1) + " out of " + str(len(filenames)) + ' (' + filename + ')')
    # Read data from csv file & format timestamp
    raw_df = pd.read_csv(filename)
    raw_df['Timestamp'] = raw_df['Timestamp'].apply(lambda x: formatTimestamp(x)) 
    
    # Create modified data frame that removes duplicate timestamps & has timestamp as index (required for resample method)
    feat_df = raw_df.set_index(['Timestamp'])
    feat_df = feat_df.sort_index()
    feat_df = feat_df[~feat_df.index.duplicated(keep='last')]
    print("Loading Runtime: " + str(time.time() - start_time)) # Loop Runtime

    #feat_df_subset = feat_df.loc[feat_df['Activity'] == "Walking"] # filter data based on activity (Controlled)

    target_hz = 40
    total_start = datetime.strptime('6/14/2018 16:03:00',  "%m/%d/%Y %H:%M:%S")
    total_end = datetime.strptime('6/14/2018  17:38:54',  "%m/%d/%Y %H:%M:%S")
    
    start_time = time.time()
    resamp_df, devices = re.resample(feat_df,total_start,total_end,target_hz)
    print("Resampling Runtime: " + str(time.time() - start_time)) # Loop Runtime
    
    absolute_start_time = time.time() # Program Start Time
    for d in range(len(devices)):
        device_name = devices[d]
        start_time = time.time()
        
        print("Device " + str(d+1) + " out of " + str(len(devices)) + ' (' + device_name + ')')
        curr_df = resamp_df[device_name]
        
        # Axis Separation
        print(".....Loading Data.....")
        x = curr_df['X']
        y = curr_df['Y']
        z = curr_df['Z']
        
        pid = curr_df['PID']
        pid = [p if p=='Unknown' else p[4:] for p in pid]
        act = curr_df['Activity']
        act[pd.isna(act)] = 'Unknown'
        pos = curr_df['Device Position']
        pos[pd.isna(pos)] = 'Unknown'
        
        m = fe.mag_acc(x,y,z)
        
        # Time Windowing
        print(".....Segmenting Data.....")
        overlap = 2
        window_size = target_hz * overlap
        hop = int(window_size/overlap)
        
        x = [x[i:i+window_size] for i in range(0, len(x)-window_size, hop)]
        y = [y[i:i+window_size] for i in range(0, len(y)-window_size, hop)]
        z = [z[i:i+window_size] for i in range(0, len(z)-window_size, hop)]
        m = [m[i:i+window_size] for i in range(0, len(m)-window_size, hop)]

        print("Pre-Processing Runtime: " + str(time.time() - start_time)) # Loop Runtime
        
        # Feature Dictionary
        features = {} # dictionary for calculated features
        
        # Timestamps
        print("----- Timestamp")
        features['start_timestamp'] = [datetime.strftime(curr_df.index[i],'%m-%d-%Y %H:%M:%S') for i in  range(0, len(curr_df)-window_size, hop)]
        features['end_timestamp'] = [datetime.strftime(curr_df.index[i],'%m-%d-%Y %H:%M:%S') for i in  range(window_size, len(curr_df), hop)]
        
        # Labels
        print("----- Labels")
        features['pid'] = [pid[i] for i in  range(0, len(curr_df)-window_size, hop)]
        features['activity'] = [act[i] for i in  range(0, len(curr_df)-window_size, hop)]
        features['device_position'] = [pos[i] for i in  range(0, len(curr_df)-window_size, hop)]
        
        # Mean
        print("----- Mean")
        features['mean_x'], features['mean_y'], features['mean_z'], features['mean_m'] = fe.mean_acc(x,y,z,m)
        
        # Maxium        
        print("----- Maximum")
        features['max_x'], features['max_y'], features['max_z'], features['max_m'] = fe.max_acc(x,y,z,m)
        
        # Minimum
        print("----- Minimum")
        features['min_x'], features['min_y'], features['min_z'], features['min_m'] = fe.min_acc(x,y,z,m)
        
        # Median
        print("----- Median")
        features['median_x'], features['median_y'], features['median_z'], features['median_m'] = fe.median_acc(x,y,z,m)
        
        # Standard Deviation
        print("----- Standard Deviation")
        features['std_x'], features['std_y'], features['std_z'], features['std_m'] = fe.std_acc(x,y,z,m)
        
        # Energy
        print("----- Energy")
        features['energy_x'], features['energy_y'], features['energy_z'], features['energy_m'] = fe.energy_acc(x,y,z,m)
                
        # Skewness
        print("----- Entropy")
        features['entropy_x'], features['entropy_y'], features['entropy_z'], features['entropy_m'] = fe.entropy_acc(x,y,z,m)

        # Median Absolute Deviation
        print("----- Median Absolute Deviation")
        features['mad_x'], features['mad_y'], features['mad_z'], features['mad_m'] = fe.mad_acc(x,y,z,m)
        
        # Percentiles
        for i in range(5,100,5):
            print("----- "+str(i)+"th Percentile")
            features['perc'+str(i)+'_x'], features['perc'+str(i)+'_y'], features['perc'+str(i)+'_z'], features['perc'+str(i)+'_m'] = fe.perc_acc(x,y,z,m,i)
        
        # IQR
        print("----- Inter-Quartile Range")
        features['iqr_x'], features['iqr_y'], features['iqr_z'], features['iqr_m'] = fe.iqr_acc(x,y,z,m)
                
        # Peak-to-Peak Ampltitude
        print("----- Peak-to-Peak Ampltitude")
        features['ptop_x'], features['ptop_y'], features['ptop_z'], features['ptop_m'] = fe.ptop_acc(x,y,z,m)
                
        # Zero-crossing rate
        print("----- Zero-crossing rate")
        features['zcr_x'], features['zcr_y'], features['zcr_z'], features['zcr_m'] = fe.zcr_acc(x,y,z,m)
                   
        # Mean-crossing rate
        print("----- Mean-crossing rate")
        features['mcr_x'], features['mcr_y'], features['mcr_z'], features['mcr_m'] = fe.mcr_acc(x,y,z,m)
                     
        # Maxium Index   
        print("----- Maximum Index")
        features['maxind_x'], features['maxind_y'], features['maxind_z'], features['maxind_m'] = fe.maxind_acc(x,y,z,m)
        
        # Minimum Index
        print("----- Minimum Index")
        features['minind_x'], features['minind_y'], features['minind_z'], features['minind_m'] = fe.minind_acc(x,y,z,m)
        
        # Signal Magnitude Area
        print("----- Signal Magnitude Area")
        features['sma'] = fe.sma_acc(x,y,z)

        # Signal Vector Magnitude
        print("----- Signal Vector Magnitude")
        features['svm'] = fe.svm_acc(x,y,z)
           
        # Kurtosis
        print("----- Kurtosis")
        features['kurtosis_x'], features['kurtosis_y'], features['kurtosis_z'], features['kurtosis_m'] = fe.kurt_acc(x,y,z,m)
                   
        # Skewness
        print("----- Skewness")
        features['skew_x'], features['skew_y'], features['skew_z'], features['skew_m'] = fe.skew_acc(x,y,z,m)

        # Pairwise Axis Correlation
        print("----- Pairwise Axis Correlation")
        features['cor_xy'], features['cor_yz'], features['cor_xz'] = fe.cor_acc(x,y,z)
          
        final_feat = pd.DataFrame.from_dict(features)
        filename = target_path+'/'+device_name+'_feat.csv'
        final_feat.to_csv(filename, sep=',', encoding='utf-8')
    
        print("Feature Extraction Runtime: " + str(time.time() - start_time)) # Loop Runtime
    
print("Total Program Runtime: " + str(time.time() - absolute_start_time)) # Program End Time

