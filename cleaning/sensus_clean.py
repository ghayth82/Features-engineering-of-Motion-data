#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 09:59:20 2018

@author: sm7gc

Data cleaning script that separates raw Sensus data (from JSON files) per probe into corresponding CSV

"""


import json 
import os
import csv
import time

  
# List of Device ID and Device Name pairs (ADD DEVICES AS NEEDED)
device_dict = {"0d3a7c5044a5cc33": "Pixel2-walleye",
               "fde44c748cd186a7":"Pixel2-taimen",
               "A8375B1A-9B7E-4AFB-9E59-C0FFFBA294B8":"iPhone8.1",
               "1a4cc41424b4d2a2":"LGE-elsa",
               "5B668C42-B351-471B-BE64-9D485477A0EF":"iPhone9.1",
               "6DD4FF11-386A-4092-B849-F8C3D1E4D6C5":"iPhone10.1"}

data_folders = ['./../Raw/09-14-18/Controlled'] # Define data filepath(s)
target_folder = './../Labeled/09-14-18/Clean' # Define folder to store clean files

absolute_start_time = time.time()
    
for data_folder in data_folders:
    
    filenames = os.listdir(data_folder)
    
    for i in range(len(filenames)):
        
        start_time = time.time()
        
        print("File " + str(i+1) + " out of " + str(len(filenames)) + ' (' + data_folder + ')') # progress print statement

        filename = filenames[i]
        if filename.endswith(".json"):
            
            file = open(os.path.join(data_folder, filename))
            raw_data = json.load(file)
            
            for line in raw_data:
                
                if line["DeviceId"] in device_dict:
                    line["Device Model"] = device_dict[line["DeviceId"]]
                else:
                    line["Device Model"] = "Unknown"
                    
                line["Sensus OS"] = line["$type"].split(',')[1]
                line["Data Type"] = line.pop("$type").split(',')[0]
                
                if "PID" in line:
                    line.pop("PID")
                    
                data_type_split = line["Data Type"].split('.')
                data_type = data_type_split[len(data_type_split)-1]
                if data_type[-5:] == "Datum":
                    datum = data_type[:-5]
                else:
                    datum = data_type
                    
                if datum == "Activity":
                    line["Activity Mode"] = line.pop("Activity")
                    
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

                if "DeviceModel" in line:
                    line.pop("DeviceModel")
                
                if line["Device Model"] == "Smartwatch":
                    fname = target_folder + '/Smartwatch_' + datum + '.csv'
                else: 
                    fname = target_folder + '/' + datum + '.csv'

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
        
        print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " --- " %())
                
print("Total Program Runtime: " + str(time.time() - absolute_start_time))