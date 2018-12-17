#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 09:37:55 2018

@author: mob3f
"""

import time
import os
import shutil
import pandas as pd
from datetime import datetime
from dateutil import tz
import warnings
import itertools
import feature_extraction as fe
import resampling as re

warnings.filterwarnings("ignore")

# Format timestamp and convert from GMT to EST for comparison purposes
def formatTimestamp(timestamp,tz_convert=False):
    
    timestamp = timestamp[:-6]
    if len(timestamp) == 19: timestamp += '.000000'
    timestamp = datetime.strptime(timestamp,  "%Y-%m-%dT%H:%M:%S.%f")
    
    if tz_convert:
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/New_York')
        timestamp = timestamp.replace(tzinfo=from_zone)
        timestamp = timestamp.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S.%f')
        timestamp = datetime.strptime(timestamp,  "%Y-%m-%d %H:%M:%S.%f") # redundant?
        
    return timestamp

absolute_start_time = time.time() # Program Start Time

# =============================================================================
#                                   FILE I/O
# =============================================================================

start_time = time.time()
print(".....Reading Data.....")

filename = '/Users/sm7gc/Desktop/WASH/Labeled/09-14-18/Controlled/Accelerometer.csv'

# Read data from csv file & format timestamp
raw_df = pd.read_csv(filename)
print("Reading Runtime: " + str(time.time() - start_time)) # Loop Runtime

# =============================================================================
#                              DATAFAME FORMATTING
# =============================================================================

start_time = time.time()
# Create modified data frame that removes duplicate timestamps & has timestamp as index (required for resample method)
feat_df = raw_df.set_index(['Timestamp'])
feat_df.index = pd.Series(feat_df.index).apply(lambda x: formatTimestamp(x))
feat_df = feat_df.sort_index()
feat_df = feat_df[~feat_df.index.duplicated(keep='last')]
print("Pre-Processing Runtime: " + str(time.time() - start_time)) # Loop Runtime

# =============================================================================
#                                 RESAMPLING
# =============================================================================

target_hz = 40
overlap = 2
window_size = target_hz * 2
hop = int(window_size/overlap)
sep = 'Sensus OS' # 'Device ID' or 'Sensus OS'
datetime_range = [['2018-9-13 17:31:35','2018-9-13 17:48:35'],['2018-9-14 14:34:32','2018-9-14 15:49:19'],['2018-9-14 19:27:19','2018-9-14 19:57:48']] # enter precise data collection datetime ranges

start_time = time.time()
resamp_df, keys = re.resample(feat_df,target_hz,sep,datetime_range)
print("Resampling Runtime: " + str(time.time() - start_time)) # Loop Runtime

    
# =============================================================================
#                             FEATURE EXTRACTION
# =============================================================================


target_path = '/Users/sm7gc/Desktop/WASH/Featurized/09-14-18/OS&Participant' if sep == 'Sensus OS' else '/Users/sm7gc/Desktop/WASH/Featurized/09-14-18/Device'
shutil.rmtree(target_path)
os.makedirs(target_path)

features = {} # dictionary for calculated features

for k in range(len(keys)):
    key = keys[k]
    start_time = time.time()
    
    print(str(k+1) + " out of " + str(len(keys)) + ' (' + key + ')')
    
    
    print(".....Loading Data.....")
    curr_df = resamp_df[key]
    
    pid = curr_df['PID']
    pid[pd.isna(pid)] = 'Unknown'
    act = curr_df['Activity']
    act[pd.isna(act)] = 'Unknown'
    pos = curr_df['Device Position']
    pos[pd.isna(pos)] = 'Unknown'
    devid = curr_df['DeviceId']
    devid[pd.isna(devid)] = 'Unknown'
    
    
    # Timestamps
    print("----- Timestamp")
    features['start_timestamp'] = [datetime.strftime(curr_df.index[i],'%m-%d-%Y %H:%M:%S') for i in  range(0, len(curr_df)-window_size, hop)]
    features['end_timestamp'] = [datetime.strftime(curr_df.index[i],'%m-%d-%Y %H:%M:%S') for i in  range(window_size, len(curr_df), hop)]
    
    # Labels
    print("----- Labels")        
    features['pid'], features['activity'], features['device_position'], features['device_id'] = [], [], [], []
    for i in range(0, len(curr_df)-window_size, hop):
        pid_i = list(pid[i:i+window_size])
        features['pid'].append(max(set(pid_i), key=pid_i.count))
        
        act_i = list(act[i:i+window_size])
        features['activity'].append(max(set(act_i), key=act_i.count))
        
        pos_i = list(pos[i:i+window_size])
        features['device_position'].append(max(set(pos_i), key=pos_i.count))
        
        devid_i = list(devid[i:i+window_size])
        features['device_id'].append(max(set(devid_i), key=devid_i.count))
    
    print("Pre-Processing Runtime: " + str(time.time() - start_time)) # Loop Runtime
    
    # Axis Separation
    x = curr_df['X']
    y = curr_df['Y']
    z = curr_df['Z']
    
    m = fe.mag_acc(x,y,z)
    
    # Time Windowing
    print(".....Segmenting Data.....")
    x = [x[i:i+window_size] for i in range(0, len(x)-window_size, hop)]
    y = [y[i:i+window_size] for i in range(0, len(y)-window_size, hop)]
    z = [z[i:i+window_size] for i in range(0, len(z)-window_size, hop)]
    m = [m[i:i+window_size] for i in range(0, len(m)-window_size, hop)]
    
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
            
    # Entropy
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
    
    
    # MFCC Coefficients
    print("----- MFCC Coefficients")
    mfcc_x, mfcc_y, mfcc_z, mfcc_m = fe.mfcc_acc(x,y,z,m)
    for j in range(len(mfcc_x[0])):
        features['mfcc'+str(j+1)+'_x'] = [mfcc_x[i].item(j) for i in range(len(mfcc_x))]
        features['mfcc'+str(j+1)+'_y'] = [mfcc_y[i].item(j) for i in range(len(mfcc_y))]
        features['mfcc'+str(j+1)+'_z'] = [mfcc_z[i].item(j) for i in range(len(mfcc_z))]
        features['mfcc'+str(j+1)+'_m'] = [mfcc_m[i].item(j) for i in range(len(mfcc_m))]
        
    # FFT Coefficients
    print("----- FFT Coefficients")
    fft_x, fft_y, fft_z, fft_m = fe.fft_acc(x,y,z,m)
    for j in range(len(fft_x[0])):
        features['fft'+str(j+1)+'_x'] = [fft_x[i].item(j) for i in range(len(fft_x))]
        features['fft'+str(j+1)+'_y'] = [fft_y[i].item(j) for i in range(len(fft_y))]
        features['fft'+str(j+1)+'_z'] = [fft_z[i].item(j) for i in range(len(fft_z))]
        features['fft'+str(j+1)+'_m'] = [fft_m[i].item(j) for i in range(len(fft_m))]
      
    # ----- WRITING DATAFRAME TO FILE -----
        
    final_feat = pd.DataFrame.from_dict(features)
    
    final_feat = final_feat[final_feat.start_timestamp.str[0:10] == final_feat.end_timestamp.str[0:10]]
    
    # Subsetting by participant and OS
    if sep == 'Device ID':
        filename = target_path+'/'+key+'_feat.csv'
        final_feat.to_csv(filename, sep=',', encoding='utf-8',index=False)
    else:
        feat_grouper = final_feat.groupby('pid')
        participants = list(final_feat.groupby("pid").groups)
        pairs = list(itertools.product(participants,[key]))          
        
        for p in pairs:
            pid = p[0]
            op_sys = p[1].replace(" Sensus","")
            filename = target_path+'/'+pid+'_'+op_sys+'_feat.csv'
            sep_df = feat_grouper.get_group(pid)
            print(len(sep_df))
            sep_df.to_csv(filename, sep=',', encoding='utf-8',index=False)
    
    print("Feature Extraction Runtime: " + str(time.time() - start_time)) # Loop Runtime

print("Total Program Runtime: " + str(time.time() - absolute_start_time)) # Program End Time
