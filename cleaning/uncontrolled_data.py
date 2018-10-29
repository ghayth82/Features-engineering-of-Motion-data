#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 14:40:39 2018

@author: sm7gc

Initial script for cleaning Controlled data specifically

"""

import json 
import os
import csv
from datetime import datetime, timedelta
from dateutil import tz
import time

# Format timestamp and convert from GMT to EST for comparison purposes
def formatTimestamp(timestamp):
    
    timestamp = timestamp[:19]
    timestamp = datetime.strptime(timestamp,  "%Y-%m-%dT%H:%M:%S")
    
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    
    timestamp = timestamp.replace(tzinfo=from_zone)
    
    timestamp = timestamp.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')
    return datetime.strptime(timestamp,  "%Y-%m-%d %H:%M:%S")

# Filepaths
data_folder = './../Raw/06-14-18/Uncontrolled' # Raw Data
target_folder = './../Labeled/06-14-18/Uncontrolled' # Clean Labeled Data

absolute_start_time = time.time() # abolsute program start time

filenames = os.listdir(data_folder) # list of raw data filenames

# --- RAW DATA FILES  ---
for i in range(len(filenames)):
    start_time = time.time()
    print("File " + str(i+1) + " out of " + str(len(filenames)) + ' ( EMA )') # progress print statement
    
    filename = filenames[i]
    if filename.endswith(".json"):
        
        file = open(os.path.join(data_folder, filename))
        raw_data = json.load(file)
        
        # --- DATUM ROWS  ---
        for line in raw_data:
            
            timestamp = formatTimestamp(line["Timestamp"]) # convert timestamp to python-friendly format
            
            # Formatting/Cleaning
            line["Sensus OS"] = line["$type"].split(',')[1]
            line["Data Type"] = line.pop("$type").split(',')[0]
            
            # Determine data type (different per datum)
            data_type_split = line["Data Type"].split('.')
            data_type = data_type_split[len(data_type_split)-1]
            datum = data_type[:-5]
            
            if datum == "Script": # handle EMA data only
                if isinstance(line["Response"],dict):
                    values = line["Response"].get("$values")
                    line["Response"] = ",".join(str(x) for x in values) # EMA Response
            else:
                continue # ignore datum if not EMA
            
            # Formatting/Cleaning
            if not data_folder == "Smartwatch":
                line["ID"] = line.pop("Id")
                line["Protocol ID"] = line.pop("ProtocolId")
                line["Build ID"] = line.pop("BuildId")
            
                if "ParticipantId" in line:
                    line.pop("ParticipantId")
                    
            if "DeviceModel" in line:
                line["Device Model"] = line.pop("DeviceModel")
                
            if "DeviceManufacturer" in line:
                line["Device Manufacturer"] = line.pop("DeviceManufacturer")
                line["Device Model"] = line.pop("Device Model")
                line["Operating System"] = line.pop("OperatingSystem")
            else:
                line["Device Manufacturer"] = ''
                line["Device Model"] = ''
                line["Operating System"] = ''
            
            # Determine corresponding file name
            if datum == "Script":
                if line["ScriptName"] == "Random":
                    fname = target_folder + '/RT_EMA.csv'
                elif line["ScriptName"] == "End of the day":
                    fname = target_folder + '/EOD_EMA.csv'
                elif line["ScriptName"] == "Acceleration based trigger questions":
                    fname = target_folder + '/AT_EMA.csv'
                else:
                    fname = target_folder + '/' + datum + '.csv'

            # Write/Append Datum to file
            if os.path.isfile(fname): 
                with open(fname, 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    values = list(line.values())
                    writer.writerow(values)
            else:
                with open(fname, 'w') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([*line])
                    values = list(line.values())
                    writer.writerow(values)
    
    elapsed_time = time.time() - start_time
    elapsed_total_time = time.time() - absolute_start_time                  
    print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " ---" % ()) # Program Runtime


# --- Create EMA Question Data Structure --- 

# EMA Questions Dict
ema_q = {}

# EOD
file = open(os.path.join(target_folder, 'EOD_EMA.csv'))
reader = csv.DictReader(file)
next(reader)
counter = 1
for row in reader:
    curr_inputid = row["InputId"]
    if curr_inputid not in ema_q.keys():
        ema_qname = 'EOD_Q'+str(counter)
        counter += 1
        ema_q[curr_inputid] = ema_qname

# RT
file = open(os.path.join(target_folder, 'RT_EMA.csv'))
reader = csv.DictReader(file)
next(reader)
counter = 1
for row in reader:
    curr_inputid = row["InputId"]
    if curr_inputid not in ema_q.keys():
        ema_qname = 'RT_Q'+str(counter)
        counter += 1
        ema_q[curr_inputid] = ema_qname

# Acceleration Trigger
file = open(os.path.join(target_folder, 'AT_EMA.csv'))
reader = csv.DictReader(file)
next(reader)
counter = 1
for row in reader:
    curr_inputid = row["InputId"]
    if curr_inputid not in ema_q.keys():
        ema_qname = 'AT_Q'+str(counter)
        counter += 1
        ema_q[curr_inputid] = ema_qname

ema_filenames = ['EOD_EMA.csv','RT_EMA.csv','AT_EMA.csv']
ema_responses = []
for ema_file in ema_filenames:
    file = open(os.path.join(target_folder, ema_file))
    reader = csv.DictReader(file)
    next(reader)
    for row in reader:
        timestamp = formatTimestamp(row["SubmissionTimestamp"])
        inputid = row["InputId"]
        response = row["Response"]
        start = timestamp - timedelta(seconds=80)
        end = timestamp - timedelta(seconds=20)
        ema_responses.append([start,end,inputid,response])



# --- RAW DATA FILES  ---
for i in range(len(filenames)):
    start_time = time.time()
    print("File " + str(i+1) + " out of " + str(len(filenames)) + ' ( SENSOR DATA )') # progress print statement
    
    filename = filenames[i]
    if filename.endswith(".json"):
        file = open(os.path.join(data_folder, filename))
        raw_data = json.load(file)
        
        # --- RAW DATA FILES  ---
        for line in raw_data:
            
            # Non-Timestamp Based Labeling
            timestamp = formatTimestamp(line["Timestamp"]) # python-friendly timestamp
            
            # Cleaning/Formatting
            line["Sensus OS"] = line["$type"].split(',')[1]
            line["Data Type"] = line.pop("$type").split(',')[0]
            
            data_type_split = line["Data Type"].split('.')
            data_type = data_type_split[len(data_type_split)-1]
            datum = data_type[:-5]
            
            # Ignore EMA
            if datum == "Script":
                continue
            
            # Formatting/Cleaning
            line["ID"] = line.pop("Id")
            line["Protocol ID"] = line.pop("ProtocolId")
            line["Build ID"] = line.pop("BuildId")
        
            if "ParticipantId" in line:
                line.pop("ParticipantId")
                    
            if "DeviceModel" in line:
                line["Device Model"] = line.pop("DeviceModel")
                
            if "DeviceManufacturer" in line:
                line["Device Manufacturer"] = line.pop("DeviceManufacturer")
                line["Device Model"] = line.pop("Device Model")
                line["Operating System"] = line.pop("OperatingSystem")
            else:
                line["Device Manufacturer"] = ''
                line["Device Model"] = ''
                line["Operating System"] = ''

            # Determine respective EMA response based on datum timestamp
            for ema_data in ema_responses:
                start = ema_data[0]
                end = ema_data[1]
                if (timestamp >= start and timestamp <= end):
                    inputid = ema_data[2]
                    response = ema_data[3]
                    qname = ema_q[inputid]
                    line[qname] = response

            # Fill in unlabeled columns
            for ema_qname in ema_q.values():
                if ema_qname not in line:
                    line[ema_qname] = 'NA'

            # Determine corresponding filename
            fname = target_folder + '/' + datum + '.csv'
                
            # Write/Append Datum to file
            if os.path.isfile(fname): 
                with open(fname, 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    values = list(line.values())
                    writer.writerow(values)
            else:
                with open(fname, 'w') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([*line])
                    values = list(line.values())
                    writer.writerow(values)
    
    elapsed_time = time.time() - start_time
    elapsed_total_time = time.time() - absolute_start_time                  
    print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " ---" % ()) # Program Runtime