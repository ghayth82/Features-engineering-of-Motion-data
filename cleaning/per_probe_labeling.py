#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 14:40:39 2018

@author: sm7gc
"""

import json 
import os
import csv
from datetime import datetime
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
    

# Helper function that determines position of device based on device id
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
      return -1
  

# Device ID -> Device Name Dict
device_dict = {"0d3a7c5044a5cc33": "Pixel2-walleye",
               "fde44c748cd186a7":"Pixel2-taimen",
               "A8375B1A-9B7E-4AFB-9E59-C0FFFBA294B8":"iPhone8.1",
               "1a4cc41424b4d2a2":"LGE-elsa",
               "5B668C42-B351-471B-BE64-9D485477A0EF":"iPhone9.1",
               "6DD4FF11-386A-4092-B849-F8C3D1E4D6C5":"iPhone10.1",
               "6fb74eec82575fcf":"Smartwatch",
               "c6b48865bc00d278":"Smartwatch",
               "52c785cfd659de18":"Smartwatch"}

# Open csv with annotated timestamp data
with open("./../DataCollection-06-14-2018.csv") as f:
    reader = csv.reader(f)
    next(reader) # skip header
    data = [r for r in reader]

# Getting start/end timestamps for activities 
pid_timestamps = []
pid_index = []
activity_timestamps = []
for row in data[1:]:
#    if not row[3] in pid_index:
#        pid_index.append(row[3])
#        pid_timestamps.append([row[3],row[4],row[13]])
#    else:
#        pid_timestamps[pid_index.index(row[3])][2] = row[13]
#                
#    activity_timestamps.append([row[4],row[5],"Standing",row[0],row[1],row[2],row[3]])
#    activity_timestamps.append([row[6],row[7],"Walking",row[0],row[1],row[2],row[3]])
#    if row[2] == "hand-using the phone":
#        activity_timestamps.append([row[8],row[9],"Jogging",row[0],row[1],"Pocket",row[3]])
#        activity_timestamps.append([row[10],row[11],"Jumping",row[0],row[1],"Pocket",row[3]])
#    else:
#    activity_timestamps.append([row[8],row[9],"Jogging",row[0],row[1],row[2],row[3]])
#    activity_timestamps.append([row[10],row[11],"Jumping",row[0],row[1],row[2],row[3]])
#    if row[2] == "hand-walking":
#        activity_timestamps.append([row[12],row[13],"Sitting",row[0],row[1],"On Table",row[3]])
#    else:
#        activity_timestamps.append([row[12],row[13],"Sitting",row[0],row[1],row[2],row[3]])
        
    if not row[2] in pid_index:
        pid_index.append(row[2])
        pid_timestamps.append([row[2],row[3],row[12]])
    else:
        pid_timestamps[pid_index.index(row[2])][2] = row[12]
                
    activity_timestamps.append([row[3],row[4],"Standing",row[0],row[1],row[2]])
    activity_timestamps.append([row[5],row[6],"Walking",row[0],row[1],row[2]])
    if row[7] != '':
        if row[2] == "hand-using the phone":
            activity_timestamps.append([row[7],row[8],"Jogging",row[0],row[1],"Pocket"])
        else:
            activity_timestamps.append([row[7],row[8],"Jogging",row[0],row[1],row[2]])
    if row[9] != '':   
        activity_timestamps.append([row[9],row[10],"Jumping",row[0],row[1],row[2]])
    if row[2] == "hand-walking":
        activity_timestamps.append([row[11],row[12],"Sitting",row[0],"On Table",row[2]])
    else:
        activity_timestamps.append([row[11],row[12],"Sitting",row[0],row[1],row[2]])
    
    
    
#data_collection ={'first':[datetime.strptime("9/13/18 17:31:35",  "%m/%d/%y %H:%M:%S"),datetime.strptime("9/13/18 17:48:54",  "%m/%d/%y %H:%M:%S")],
#                  'second':[datetime.strptime("9/14/18 14:34:32",  "%m/%d/%y %H:%M:%S"),datetime.strptime("9/14/18 15:49:19",  "%m/%d/%y %H:%M:%S")],
#                  'third':[datetime.strptime("9/14/18 19:27:19",  "%m/%d/%y %H:%M:%S"),datetime.strptime("9/14/18 19:57:48",  "%m/%d/%y %H:%M:%S")]}    

data_collection_start = datetime.strptime("06/14/18 16:03:03",  "%m/%d/%y %H:%M:%S")
data_collection_end = datetime.strptime("06/14/18 17:38:52",  "%m/%d/%y %H:%M:%S")

# Define data file path
data_folders = ['./../Raw/06-14-18/Controlled']
target_folder = './../Labeled/06-14-18/Controlled'

absolute_start_time = time.time()
total_labeled_count = 0
total_count = 0
    
for data_folder in data_folders:
    
    filenames = os.listdir(data_folder)
    
    for i in range(len(filenames)):
        start_time = time.time()
        curr_labeled_count = 0
        curr_count = 0
        
        print("File " + str(i+1) + " out of " + str(len(filenames)) + ' (' + data_folder + ')') # progress print statement

        filename = filenames[i]
        if filename.endswith(".json"):
            
            file = open(os.path.join(data_folder, filename))
            raw_data = json.load(file)
            for line in raw_data:
                
                # Non-Timestamp Based Labeling
                timestamp = formatTimestamp(line["Timestamp"])
#                timestamp = datetime.strptime(line["Timestamp"][:19],  "%Y-%m-%dT%H:%M:%S")
                line["Sensus OS"] = line["$type"].split(',')[1]
                line["Data Type"] = line.pop("$type").split(',')[0]
                
                data_type_split = line["Data Type"].split('.')
                data_type = data_type_split[len(data_type_split)-1]
                if data_type[-5:] == "Datum":
                    datum = data_type[:-5]
                else:
                    datum = data_type
                
                if line["DeviceId"] in device_dict:
                    line["Device Model"] = device_dict[line["DeviceId"]]
                else:
                    line["Device Model"] = "Unknown"
                
#                if line["Device Model"] != "Smartwatch":
#                    continue
            
                if "PID" in line:
                    line.pop("PID")
    
                if datum == "Activity":
                    line["Activity Mode"] = line.pop("Activity")
                        
#                if (timestamp >= data_collection['first'][0] and timestamp <= data_collection['first'][1]) or (timestamp >= data_collection['second'][0] and timestamp <= data_collection['second'][1]) or (timestamp >= data_collection['third'][0] and timestamp <= data_collection['third'][1]):
    
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
                            
                            curr_labeled_count += 1
                            
                            line["Activity"] = row[2]
                            
                            # -- POSITION LABELING  --
                            if "Device Model" in line and line["Device Model"] not in ['Smartwatch','Unknown']:
                                if getPosition(line["DeviceId"]) in range(len(row)):
                                    line["Device Position"] = row[getPosition(line["DeviceId"])]
                
                if not "PID" in line:
                    line["PID"] = 'NA'
                    
                if not "Activity" in line:
                    line["Activity"] = 'Unknown'
                    if not line["Device Model"] == "Smartwatch":
                        line["Device Position"] = 'Unknown'
                        
                # Making Column Names more readable and order
                if not line["Device Model"] == "Smartwatch":
                    line["ID"] = line.pop("Id")
                    line["Protocol ID"] = line.pop("ProtocolId")
                    line["Build ID"] = line.pop("BuildId")
                
                    if "ParticipantId" in line:
                        line.pop("ParticipantId")
                    else:
                        line["Participant ID"] = ""
                        
                    if "DeviceManufacturer" in line:
                        line["Device Manufacturer"] = line.pop("DeviceManufacturer")
                        line["Device Model"] = line.pop("Device Model")
                        line["Operating System"] = line.pop("OperatingSystem")
                    
                line["Activity"] = line.pop("Activity")
                line["PID"] = line.pop("PID")
                if "Device Position" in line:
                    line["Device Position"] = line.pop("Device Position")
                
                if "DeviceModel" in line:
                    line.pop("DeviceModel")
                
                if line["Device Model"] == "Smartwatch":
                    fname = target_folder + '/Smartwatch_' + datum + '.csv'
                else: 
                    fname = target_folder + '/' + datum + '.csv'
                    
                curr_count += 1
                
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

        total_count += curr_count
        total_labeled_count += curr_labeled_count

        elapsed_time = time.time() - start_time
        elapsed_total_time = time.time() - absolute_start_time        
        
        print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " --- " %())
        print(str(curr_labeled_count) +  " out of " + str(curr_count) + " labeled data\n")
                
print("Total Program Runtime: " + str(time.time() - absolute_start_time))
print(str(total_labeled_count) +  " / " + str(total_count) + " = " + str(total_labeled_count/total_count) + "% labeled")