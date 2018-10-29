#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on ???

@author: sm7gc

Initial script for cleaning Controlled data specifically

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
    
#    from_zone = tz.gettz('UTC')
#    to_zone = tz.gettz('America/New_York')
#    
#    timestamp = timestamp.replace(tzinfo=from_zone)
#    
#    timestamp = timestamp.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')
#    return datetime.strptime(timestamp,  "%Y-%m-%d %H:%M:%S")
    return timestamp
    

# Helper function that determines position of device based on device id
def getPosition(deviceid):
  if (deviceid == "60bfd1a1721a5e02" or deviceid == "09f392ab779b98fc") : # Pixel 2 (walleye/taimen)
    return 2
  elif (deviceid == "39CFD493-D958-4726-AC01-02596ADB5998") : # iPhone 9
    return 2
  elif (deviceid == "6DD4FF11-386A-4092-B849-F8C3D1E4D6C5") : # iPhone 10
    return 1
  else:
    return -1
    
# Map raw PID values to more readable format
pid_dict = {'002-Crishon': 'Crishon', '003-Lee': 'Lee', '004-Mehdi': 'Mehdi', '001-Peter': 'Peter'}

# Datum Dict for SMARTPHONES
smartphone_probe_dict = {'Sensus.Probes.Movement.AccelerometerDatum':'Accelerometer',
              'Sensus.Probes.Movement.ActivityDatum':'Activity',
              'Sensus.Probes.Location.AltitudeDatum':'Altitude',
              'Sensus.Probes.Device.BatteryDatum':'Battery',
              'Sensus.Probes.Location.CompassDatum':'Compass',
              'Sensus.Probes.Context.LightDatum':'Light',
              'Sensus.Probes.Location.LocationDatum':'Location',
              'Sensus.Probes.Device.ScreenDatum':'Screen',
              'Sensus.Probes.Context.SoundDatum':'Sound',
              'Sensus.Probes.Movement.SpeedDatum':'Speed',
              'Sensus.ParticipationReportDatum':'ParticipationReport',
              'Sensus.Probes.Network.CellTowerDatum':'CellTower'}

# Datum Dict for SMARTWATCH
smartwatch_probe_dict = {'SWear.Probes.Environment.Light':'Light',
              'SWear.Probes.Movement.GyroscopeDatum':'Gyroscope',
              'SWear.Probes.Movement.HeartRateDatum':'HeartRate',
              'SWear.Probes.Movement.LinearAccelerationDatum':'LinearAcceleration',
              'SWear.Probes.Movement.StepCountDatum':'StepCount'}

# Device ID -> Device Name Dict
device_dict = {"60bfd1a1721a5e02": "Pixel2-walleye",
               "09f392ab779b98fc":"Pixel2-taimen",
               "39CFD493-D958-4726-AC01-02596ADB5998":"iPhone9.1",
               "6DD4FF11-386A-4092-B849-F8C3D1E4D6C5":"iPhone10.1"}

# Open csv with annotated timestamp data
with open("./../DataCollection-06-14-2018.csv") as f:
    reader = csv.reader(f)
    next(reader) # skip header
    data = [r for r in reader]

# Getting start/end timestamps for activities
activity_timestamps = []
for row in data[1:]:
    activity_timestamps.append([row[3],row[4],"Standing",row[0],row[1],row[2]])
    activity_timestamps.append([row[5],row[6],"Walking",row[0],row[1],row[2]])
    if row[7] != '':
        activity_timestamps.append([row[7],row[8],"Jogging",row[0],row[1],row[2]])
    if row[9] != '':
        activity_timestamps.append([row[9],row[10],"Jumping",row[0],row[1],row[2]])
    activity_timestamps.append([row[11],row[12],"Sitting",row[0],row[1],row[2]])
    
# Define data file path
data_folder = ['./../Controlled','./../Smartwatch']
target_folder = 'Controlled-Labeled Probe Data'
filenames = os.listdir(data_folder)
#filenames =['e076c9f2-1270-4ac1-8d81-cc76c13049e9.json'] # Controlled Test File

absolute_start_time = time.time()

for i in range(len(filenames)):
    start_time = time.time()
    print("File " + str(i+1) + " out of " + str(len(filenames))) # progress print statement
    
    filename = filenames[i]
    if filename.endswith(".json"):
        file = open(os.path.join(data_folder, filename))
        raw_data = json.load(file)
        for line in raw_data:
            
            # Non-Timestamp based labeling
            timestamp = formatTimestamp(line["Timestamp"])
            line["Sensus OS"] = line["$type"].split(',')[1]
            line["Data Type"] = line.pop("$type").split(',')[0]
            
            if data_folder == "Controlled":
                datum = smartphone_probe_dict[line["Data Type"]]            
                if line["DeviceId"] in device_dict:
                    line["Device Model"] = device_dict[line["DeviceId"]]
                else:
                    line["Device Model"] = "Unknown"
            elif data_folder == "Smartwatch":
                datum = smartwatch_probe_dict[line["Data Type"]]
                line["Device Model"] = "Smartwatch"
            
            device = line["Device Model"]

            # Determine Label
            for row in activity_timestamps:
                
                start = datetime.strptime(row[0],  "%m/%d/%y %H:%M:%S")
                end = datetime.strptime(row[1],  "%m/%d/%y %H:%M:%S")
                
                if (timestamp >= start and timestamp <= end):
                    print(timestamp)
#                    if datum == "Activity":
#                        line["Activity Mode"] = line.pop("Activity")
#                    line["Activity"] = row[2]
#                    line["PID"] = row[5]
#                    
#                    pid = pid_dict[line["PID"]]
#                    
#                    # -- POSITION LABELING FOR SMARTPHONES --
#                    if "Device Model" in line:
#                        if not line["Device Model"] == 'Smartwatch':
#                            if getPosition(line["DeviceId"]) == 1:
#                                line["Device Position"] = row[3]
#                            elif getPosition(line["DeviceId"]) == 2:
#                                line["Device Position"] = row[4]
#                            else:
#                                line["Device Position"] = 'Unknown'
#                    else:
#                        line["Device Position"] = 'Unknown'
#            
#            if not "PID" in line:
#                if datum == "Activity":
#                    line["Activity Mode"] = line.pop("Activity")
#                line["Activity"] = 'Unknown'
#                line["PID"] = 'NA'
#                if not data_folder == "Smartwatch":
#                    line["Device Position"] = 'Unknown'
#                    
#            # Making Column Names more readable and order
#            if not data_folder == "Smartwatch":
#                line["ID"] = line.pop("Id")
#                line["Protocol ID"] = line.pop("ProtocolId")
#                line["Build ID"] = line.pop("BuildId")
#            
#                if "ParticipantId" in line:
#                    line.pop("ParticipantId")
#                else:
#                    line["Participant ID"] = ""
#                    
#                if "DeviceManufacturer" in line:
#                    line["Device Manufacturer"] = line.pop("DeviceManufacturer")
#                    line["Device Model"] = line.pop("Device Model")
#                    line["Operating System"] = line.pop("OperatingSystem")
#                
#            line["Activity"] = line.pop("Activity")
#            line["PID"] = line.pop("PID")
#            if "Device Position" in line:
#                line["Device Position"] = line.pop("Device Position")
#            
#            if "DeviceModel" in line:
#                line.pop("DeviceModel")
#                
#            # Add line to appropriate csv file
#            fname = target_folder = '/' + pid + '/' + device + '/' + datum + '/' + pid + '_' + device + '_' + datum + '_labeled.csv'
#            if os.path.isfile(fname): 
#                with open(fname, 'a') as csvfile:
#                    writer = csv.writer(csvfile)
#                    values = list(line.values())
#                    writer.writerow(values)
#            else:
#                with open(fname, 'w') as csvfile:
#                    writer = csv.writer(csvfile)
#                    writer.writerow([*line])
#                    values = list(line.values())
#                    writer.writerow(values)
#    
#    elapsed_time = time.time() - start_time
#    elapsed_total_time = time.time() - absolute_start_time                  
#    print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " ---" % ())
                
                    
print("Total Program Runtime: " + str(time.time() - absolute_start_time))