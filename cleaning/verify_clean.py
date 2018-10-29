#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 09:28:37 2018

@author: sm7gc
"""

import csv
import os

data_folder = './../../Labeled/09-14-18/Controlled'
filenames = [os.path.join(dp, f) for dp, dn, filenames in os.walk(data_folder) for f in filenames if os.path.splitext(f)[1] == '.csv']

error_files = set()
error_keys = set()
got_len = False
ncol = 0
for csv_file in filenames:
    print(csv_file)
    with open(csv_file) as f:
        r = csv.DictReader(f)
        for line in r:
#            print(line.keys())
            if not got_len:
                ref_col = line
                ncol = len(line)
                got_len = True
            if not len(line) == ncol:
                error_files.add(csv_file)
                error_keys.add(set(ref_col)-set(line))
        got_len = False