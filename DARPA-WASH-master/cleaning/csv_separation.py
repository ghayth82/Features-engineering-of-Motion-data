#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 17:12:28 2018

@author: sm7gc

Seperate probe-separated CSV data by PID & device

"""


import os
import csv

pid_dict = {'002-Crishon': 'Crishon', '003-Lee': 'Lee', '004-Mehdi': 'Mehdi', '001-Peter':'Peter'}
device_dict = {'taimen':'Pixel2-taimen', 'walleye':'Pixel2-walleye', 'iPhone9.1':'iPhone9.1', 'iPhone10.1':'iPhone10.1', 'NA':'Unknown', '':'Unknown'}
datum_dict = {'Sensus.Probes.Movement.AccelerometerDatum':'Accelerometer',
              'Sensus.Probes.Movement.ActivityDatum':'Activity',
              'Sensus.Probes.Location.AltitudeDatum':'Altitude',
              'Sensus.Probes.Device.BatteryDatum':'Battery',
              'Sensus.Probes.Location.CompassDatum':'Compass',
              'Sensus.Probes.Context.LightDatum':'Light',
              'Sensus.Probes.Location.LocationDatum':'Location',
              'Sensus.Probes.Device.ScreenDatum':'Screen',
              'Sensus.Probes.Context.SoundDatum':'Sound',
              'Sensus.Probes.Movement.SpeedDatum':'Speed'}



filenames = os.listdir("per_probe")
for file in filenames:
    
    if file.endswith(".csv"):
        with open(os.path.join("per_probe",file)) as f:
            reader = csv.reader(f)
            data = [r for r in reader]
        
        print(file)
        
        header = data[0]
        pid_index = header.index("PID")
        device_index = header.index("Device Model")
        datum_index = header.index("Data Type")
        
        for row in data[1:]: 
            raw_pid = row[pid_index]
            raw_device = row[device_index]
            raw_datum = row[datum_index]
            
            pid = pid_dict[raw_pid]
            device = device_dict[raw_device]
            datum = datum_dict[raw_datum]
        
            fname = 'Controlled/Controlled-Labeled/' + pid + '/' + device + '/' + datum + '/' + pid + '_' + device + '_' + datum + '_labeled.csv'
#                print(fname)
            if os.path.isfile(fname): 
                with open(fname, 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(row)
            else:
                with open(fname, 'w') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(header)
                    writer.writerow(row)
                    
                        
            
        

        
        