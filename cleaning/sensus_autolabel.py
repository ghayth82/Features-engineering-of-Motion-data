#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 09:31:34 2018

@author: sm7gc

Increased automization version of sensus_clean.py

"""

import json 
import os
import csv
from datetime import datetime
from dateutil import tz
import time
import shutil
import gzip
from collections import defaultdict


#  ---- HELPER FUNCTIONS ---- 

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError:
    return False
  return True

# Format timestamp and convert from GMT to EST for comparison purposes
def formatTimestamp(timestamp):
    
    timestamp = timestamp[:19]
    timestamp = datetime.strptime(timestamp,  "%Y-%m-%dT%H:%M:%S")
    
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    
    timestamp = timestamp.replace(tzinfo=from_zone)
    
    timestamp = timestamp.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')
    return datetime.strptime(timestamp,  "%Y-%m-%d %H:%M:%S")


# Helper function that determines position of device based on device id (NEED TO CUSTOMIZE BASED ON DATACOLLECTION CSV)
def getPosition(deviceid):
  if deviceid == "fde44c748cd186a7": # Device 1
      return 3
  elif deviceid == "6DD4FF11-386A-4092-B849-F8C3D1E4D6C5": # Device 2
      return 3
  elif deviceid == "0d3a7c5044a5cc33": # Device 3
      return 4
  elif deviceid == "A8375B1A-9B7E-4AFB-9E59-C0FFFBA294B8": # Device 4
      return 4
  elif deviceid == "1a4cc41424b4d2a2": # Device 5
      return 5
  elif deviceid == "5B668C42-B351-471B-BE64-9D485477A0EF": # Device 6
      return 5
  else:
      return 'NA'

# DataCollection csv with annotated timestamp data
with open("/Users/sm7gc/Desktop/WASH/DataCollection-06-14-2018.csv") as f:
    reader = csv.reader(f)
    header = next(reader)
    data = [r for r in reader]

# Activity/PID Timestamp Lists
activity_timestamps = []
pid_timestamps = []
pid_index = []

pid_col = 3 # Define which column of DataCollection csv contains PID
for row in data[2:]:
    
    curr_pid = row[pid_col-1][4:]
    
    # Absolute Start/End per PID
    if not curr_pid in pid_index: # if PID has not been added to pid_timestamps
        pid_index.append(curr_pid) # add to running list of added PIDs
        pid_timestamps.append([curr_pid,row[pid_col],row[len(row)-1]]) # 
    else:
        pid_timestamps[pid_index.index(curr_pid)][2] = row[len(row)-1]
                
    # Start/End per Activity + Device Positions
    for i in range(pid_col,len(row),2):
        activity = header[i]
        if row[i] == "": 
            continue
        activity_row = [row[i],row[i+1],header[i]]
        for j in range(pid_col):
            if activity == "Sitting" and row[j] == "hand-walking":
                activity_row.append("On Table")
            else:
                activity_row.append(row[j])
        activity_timestamps.append(activity_row)


#  ---- MAIN CODE ---- 

# Define absolute start and end of data collection for maximum efficiency
data_collection_start = datetime.strptime("06/14/18 16:03:03",  "%m/%d/%y %H:%M:%S")
data_collection_end = datetime.strptime("06/14/18 17:38:52",  "%m/%d/%y %H:%M:%S")


data_folder = '/Users/sm7gc/Desktop/WASH/Raw/06-14-18/Controlled/compressed' # Define data filepath(s)
target_folder = '/Users/sm7gc/Desktop/WASH/Labeled/06-14-18/Controlled_Auto' # Define folder to store clean files

absolute_start_time = time.time()

complete_data = defaultdict(list)

filenames = [os.path.join(dp, f) for dp, dn, filenames in os.walk(data_folder) for f in filenames if os.path.splitext(f)[1] == '.gz']


for i in range(len(filenames)):
    
    file = filenames[i]

    print("File " + str(i+1) + " out of " + str(len(filenames)) + ' (' + data_folder + ')') # progress print statement
    
    start_time = time.time()
    
    f = gzip.open(file, 'rb')
    file_content = f.read()
    if not is_json(file_content):
        continue
    raw_data = json.loads(file_content)

    base = ''
    if 'Swear' in file:
        base = 'Smartwatch_'

    for line in raw_data:
        
        line["Sensus OS"] = line["$type"].split(',')[1]
        line["Data Type"] = line.pop("$type").split(',')[0]
        
        if "PID" in line:
            line.pop("PID")
            
        init_line = line
        init_len = len(line)
        
        data_type_split = line["Data Type"].split('.')
        data_type = data_type_split[len(data_type_split)-1]
        if data_type[-5:] == "Datum":
            datum = data_type[:-5]
        else:
            datum = data_type
            
        file = base + datum + '.csv'
        
        if datum == "Activity":
            line["Activity Mode"] = line.pop("Activity")

        timestamp = formatTimestamp(line['Timestamp'])

        if timestamp >= data_collection_start and timestamp <= data_collection_end:
                    
            for row in pid_timestamps:
                start = datetime.strptime(row[1],  "%m/%d/%y %H:%M:%S")
                end = datetime.strptime(row[2],  "%m/%d/%y %H:%M:%S")
                if (timestamp >= start and timestamp <= end):
                    line["PID"] = row[0]
                
            # Determine Label
            for row in activity_timestamps:
                
                start = datetime.strptime(row[0],  "%m/%d/%y %H:%M:%S")
                end = datetime.strptime(row[1],  "%m/%d/%y %H:%M:%S")
                
                if (timestamp >= start and timestamp <= end):
                    
                    line["Activity"] = row[2]
                    
                    # -- POSITION LABELING  --
                    if "DeviceId" in line and 'Swear' not in file:
                        if getPosition(line["DeviceId"]) in range(len(row)):
                            line["Device Position"] = row[getPosition(line["DeviceId"])]
                        else:
                            line["Device Position"] = 'Unknown'
                
#        line["Device Number"] = getPosition(line["DeviceId"])
        
        if not "PID" in line:
            line["PID"] = 'NA'
            
        if not "Activity" in line:
            line["Activity"] = 'Unknown'
            if 'Swear' not in file:
                line["Device Position"] = 'Unknown'
                
        # Making Column Names more readable and order
        if "DeviceManufacturer" in line:
            
            line["ID"] = line.pop("Id")
            line["Protocol ID"] = line.pop("ProtocolId")
            line["Build ID"] = line.pop("BuildId")
        
            if "ParticipantId" in line:
                line.pop("ParticipantId")
            else:
                line["Participant ID"] = ""
                
            line["Device Manufacturer"] = line.pop("DeviceManufacturer")
#            line["Device Model"] = line.pop("Device Model")
            if "DeviceModel" in line:
                line.pop("DeviceModel")    
            elif "Device Model" in line:
                line.pop("Device Model")
            line["Operating System"] = line.pop("OperatingSystem")
            
        line["Activity"] = line.pop("Activity")
        line["PID"] = line.pop("PID")
        if "Device Position" in line:
            line["Device Position"] = line.pop("Device Position")
        
        complete_data[file].append(line)

    elapsed_time = time.time() - start_time
    elapsed_total_time = time.time() - absolute_start_time        
    
    print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " --- " %())

shutil.rmtree(target_folder)
os.makedirs(target_folder)

absolute_start_time = time.time()           
for key in complete_data.keys():
    if key is 'ParticipationReport.csv': continue
    
    print(key + ' (' + str(len(complete_data[key])) + ')') # progress print statement
    start_time = time.time()
    with open(os.path.join(target_folder,key),'w') as f:
        writer = csv.DictWriter(f, fieldnames=complete_data[key][0].keys())
        writer.writeheader()
        writer.writerows(complete_data[key])
        f.close()
        
    elapsed_time = time.time() - start_time
    elapsed_total_time = time.time() - absolute_start_time        
    
    print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " --- " %())

print("Total Program Runtime: " + str(time.time() - absolute_start_time))