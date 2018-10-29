#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 14:19:37 2018

@author: sm7gc

Test script for how to parse EMA data from raw ScriptRun (?)

"""

import csv

# Read RT EMA data
with open('Uncontrolled - Clean Probe CSV/RT_EMA.csv') as f:
    reader = csv.reader(f)
    header = next(reader) # skip header
    ema_data = [r for r in reader]
    
# Get column indices
response_index = header.index('Response')
inputid_index = header.index('InputId')
timestamp_index = header.index('RunTimestamp')

# Getting start/end timestamps for motions from RT EMA
curr_runid = ''
prev_runid = ''
activity_timestamps = []
for row in ema_data:
    if row[inputid_index] == '1df9aaae-06a3-4449-88d8-00a5eeac96bd':
        activity_timestamps.append([row[timestamp_index],row[response_index]])
    elif row[inputid_index] == '3d79e2d6-3fca-4afc-a2b8-af24285f1e03':
        activity_timestamps[len(activity_timestamps)-1].append(row[response_index])

print(activity_timestamps)
        