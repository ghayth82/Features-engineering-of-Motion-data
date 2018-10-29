# Source Repository: https://github.com/seanmullane/DS6999_HAR
import glob
from astropy.stats import median_absolute_deviation
import numpy as np
import os
import pandas as pd
from scipy.stats import pearsonr
from scipy.stats import entropy
from scipy.stats import skew
from scipy.stats import kurtosis

#Set home directory for relative paths, comment in/out as needed
homedir = '/Users/sm7gc/Desktop/WASH/Scripts' #Sanjana's home dir

# This is the directory where your hz data files are located
path = '/Users/sm7gc/Desktop/WASH/Labeled/06-14-18/Controlled/*.csv'
#path = os.path.join(homedir, 'data', 'hzData', '*.csv')
files = glob.glob(path)
files = files[0] # ONLY PROCESS ACCELEROMETER

# This is the directory where you want to write the new csvs to
os.chdir('/Users/sm7gc/Desktop/WASH/Featurized')
#os.chdir(os.path.join(homedir, 'data', 'FeatureData'))

# https://stackoverflow.com/questions/8930370/where-can-i-find-mad-mean-absolute-deviation-in-scipy
def mad2(arr):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variabililty of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation 
    """
    arr = np.ma.array(arr).compressed() # should be faster to not use masked arrays.
    med = np.median(arr)
    return np.median(np.abs(arr - med))

def feature_extract():

    # Counting variable to track progress
    ct = 0
    
    # Check all 4 hz files
    for name in files:
        ct += 1
        print(ct, "/", 4, name)
    
#        hz = 40
        # Set the value of hz based on the name of the file
        if '50hz' in name:
            hz = 50
        elif '25hz' in name:
            hz = 25
        elif '10hz' in name:
            hz = 10
        else:
            hz = 5
        
        # Read the csv
        df=pd.DataFrame.from_csv(name, sep=',')
        df_out = df.reset_index()
        
        # Calculations for magnitude
        df_body_acc_mag = np.sqrt(np.square(df[['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z']]).sum(axis=1)).reset_index(drop=True).rename(columns={0:'tBodyAccMag'})
        df_gravity_acc_mag = np.sqrt(np.square(df[['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z']]).sum(axis=1)).reset_index(drop=True).rename(columns={0:'tGravityAccMag'})
        df_body_gyro_mag = np.sqrt(np.square(df[['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z']]).sum(axis=1)).reset_index(drop=True).rename(columns={0:'tBodyGyroMag'})
    
        df_out['tBodyAccMag'] = df_body_acc_mag
        df_out['tGravityAccMag'] = df_gravity_acc_mag
        df_out['tBodyGyroMag'] = df_body_gyro_mag
        
        # This creates a new index between groups (of experiment ID's)
        # For example, if the first few entries of the data looked something
        # like (experiment ID's): 1 1 1 1 1 2 2 2 3 ....
        # then the new index would look something like:
        # 0 1 2 3 4 0 1 2 0 ...
        sub_index = df_out.groupby(['PID']).cumcount()
        df_out['index'] = sub_index
    
        for seconds in [1,2,3,5,10]:
            
            # Group by experiment ID AND also in sets of (seconds*hz).
            # For example, if seconds is 10 and hz is 5, then a total of
            # 10*5=50 observations are grouped together within an experiment ID.
            # And in this case, 50 observations at 5hz = 10 seconds
            group = df_out.groupby(['experimentID',sub_index//(seconds*hz)*(seconds*hz)], as_index=False)
             
            # Filter out rows that contribute to groups of less than full size
            # This seems to require recalculating indexes
            grpsize = group.size().max()
            df_out = group.filter(lambda x: len(x) >= grpsize)
            sub_index = df_out.groupby(['experimentID']).cumcount()
            df_out['index'] = sub_index
            group = df_out.groupby(['experimentID',sub_index//(seconds*hz)*(seconds*hz)], as_index=False)
            group_square = pow(df_out,2).groupby(['experimentID',sub_index//(seconds*hz)*(seconds*hz)], as_index=False)
            
            # Initilze the feature list, which is a list that contains several
            # dataframes. At the end all of these dataframes will be concatinated
            df_feature = [group['index','tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z','tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z','tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z','experimentID','userID','activityID'].first()]
    
    
            # Tracks progress
            print('Window in seconds:',seconds)
            print('Processing tBodyAcc')
    
            ####################
            # Very important note: The end product for each of these dataframes we
            # are creating should ONLY contain new columns which we want to concat
            # together with the other dataframes. AVOID repeating things like
            # experimentID because some dataframes will automatically include it.
            # You can use the .drop(columns=['experimentID']) function to do this.
            # Fruthermore, sometimes the index will be different. Again, use the
            # .reset_index(drop=True) if this occurs. The purpose of this step
            # is to append all of these dataframes to the list of dataframes,
            # df_feature, and at the end they will be concatinated. Try to get
            # as many as done as possible.
            ####################
    
            # tBodyAcc-Mean-1
            # tBodyAcc-Mean-2                
            # tBodyAcc-Mean-3
            df_feature.append(group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].mean().rename(columns={'tBodyAcc-X':'tBodyAcc-Mean-1','tBodyAcc-Y':'tBodyAcc-Mean-2','tBodyAcc-Z':'tBodyAcc-Mean-3'}).drop(columns=['experimentID']))
    
            # tBodyAcc-STD-1                 
            # tBodyAcc-STD-2                 
            # tBodyAcc-STD-3                 
            df_feature.append(group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].std().rename(columns={'tBodyAcc-X':'tBodyAcc-STD-1','tBodyAcc-Y':'tBodyAcc-STD-2','tBodyAcc-Z':'tBodyAcc-STD-3'}).drop(columns=['experimentID']))
              
            # tBodyAcc-Mad-1
            # tBodyAcc-Mad-2                 
            # tBodyAcc-Mad-3                 
            df_feature.append(pd.DataFrame(group['tBodyAcc-X'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyAcc-X':'tBodyAcc-Mad-1'}).reset_index(drop=True)).rename(columns={0:'tBodyAcc-Mad-1'}))
            df_feature.append(pd.DataFrame(group['tBodyAcc-Y'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyAcc-Y':'tBodyAcc-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tBodyAcc-Mad-2'}))
            df_feature.append(pd.DataFrame(group['tBodyAcc-Z'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyAcc-Z':'tBodyAcc-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tBodyAcc-Mad-3'}))
                    
            # tBodyAcc-Max-1
            # tBodyAcc-Max-2                 
            # tBodyAcc-Max-3                 
            df_feature.append(group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].max().rename(columns={'tBodyAcc-X':'tBodyAcc-Max-1','tBodyAcc-Y':'tBodyAcc-Max-2','tBodyAcc-Z':'tBodyAcc-Max-3'}).drop(columns=['experimentID']))
    
            # tBodyAcc-Min-1                 
            # tBodyAcc-Min-2                 
            # tBodyAcc-Min-3                 
            df_feature.append(group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].min().rename(columns={'tBodyAcc-X':'tBodyAcc-Min-1','tBodyAcc-Y':'tBodyAcc-Min-2','tBodyAcc-Z':'tBodyAcc-Min-3'}).drop(columns=['experimentID']))
    
            # tBodyAcc-SMA-1
            # https://www.hindawi.com/journals/mpe/2015/790412/
            x=group['tBodyAcc-X'].apply(lambda x:list(x)).reset_index(drop=True)
            y=group['tBodyAcc-Y'].apply(lambda x:list(x)).reset_index(drop=True)
            z=group['tBodyAcc-Z'].apply(lambda x:list(x)).reset_index(drop=True)
            
            x=pd.DataFrame(x.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            y=pd.DataFrame(y.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            z=pd.DataFrame(z.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            
            sma=(x+y+z).rename(columns={0:'tBodyAcc-SMA-1'})
            df_feature.append(sma)
            
            # tBodyAcc-Energy-1
            # tBodyAcc-Energy-2              
            # tBodyAcc-Energy-3
            a=group_square['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].sum().drop(columns=['experimentID'])
            b=group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].count().drop(columns=['experimentID'])
            df_feature.append((a/b).rename(columns={'tBodyAcc-X':'tBodyAcc-Energy-1','tBodyAcc-Y':'tBodyAcc-Energy-2','tBodyAcc-Z':'tBodyAcc-Energy-3'}))
            
            # tBodyAcc-IQR-1         
            # tBodyAcc-IQR-2                 
            # tBodyAcc-IQR-3      
            a=group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].quantile(0.75).reset_index(drop=True)
            b=group['tBodyAcc-X','tBodyAcc-Y','tBodyAcc-Z'].quantile(0.25).reset_index(drop=True)
            df_feature.append((a-b).rename(columns={'tBodyAcc-X':'tBodyAcc-IQR-1','tBodyAcc-Y':'tBodyAcc-IQR-2','tBodyAcc-Z':'tBodyAcc-IQR-3'}))
            
            # tBodyAcc-ropy-1                
            # tBodyAcc-ropy-2
            # tBodyAcc-ropy-3   
            x=pd.DataFrame(group['tBodyAcc-X'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyAcc-ropy-1'})
            y=pd.DataFrame(group['tBodyAcc-Y'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyAcc-ropy-2'})
            z=pd.DataFrame(group['tBodyAcc-Z'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyAcc-ropy-3'})
            df_feature.append(x)
            df_feature.append(y)
            df_feature.append(z)
    
            # tBodyAcc-ARCoeff-1             
            # tBodyAcc-ARCoeff-2             
            # tBodyAcc-ARCoeff-3             
            # tBodyAcc-ARCoeff-4    
            a=group['tBodyAcc-X'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tBodyAcc-X'].count()['tBodyAcc-X']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-4'}))
            
            # tBodyAcc-ARCoeff-5             
            # tBodyAcc-ARCoeff-6             
            # tBodyAcc-ARCoeff-7             
            # tBodyAcc-ARCoeff-8
            a=group['tBodyAcc-Y'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tBodyAcc-Y'].count()['tBodyAcc-Y']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-5'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-6'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-7'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-8'}))        
    
            # tBodyAcc-ARCoeff-9             
            # tBodyAcc-ARCoeff-10            
            # tBodyAcc-ARCoeff-11            
            # tBodyAcc-ARCoeff-12
            a=group['tBodyAcc-Z'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tBodyAcc-Z'].count()['tBodyAcc-Z']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-9'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-10'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-11'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAcc-ARCoeff-12'}))
            
            # tBodyAcc-Correlation-1         
            # tBodyAcc-Correlation-2         
            # tBodyAcc-Correlation-3
            x=pd.DataFrame(group['tBodyAcc-X'].apply(lambda x:list(x))).reset_index(drop=True)
            y=pd.DataFrame(group['tBodyAcc-Y'].apply(lambda x:list(x))).reset_index(drop=True)
            z=pd.DataFrame(group['tBodyAcc-Z'].apply(lambda x:list(x))).reset_index(drop=True)
            
            yz=pd.concat([y,z],axis=1)
            yz.columns = ['y','z']
            yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tBodyAcc-Correlation-1'}))
            
            xz=pd.concat([x,z],axis=1)
            xz.columns = ['x','z']
            xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tBodyAcc-Correlation-2'}))
    
            xy=pd.concat([x,y],axis=1)
            xy.columns = ['x','y']
            xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
            df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tBodyAcc-Correlation-3'}))
            
            print('Processing tGravityAcc')
            
            # tGravityAcc-Mean-1             
            # tGravityAcc-Mean-2             
            # tGravityAcc-Mean-3  
            df_feature.append(group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].mean().rename(columns={'tGravityAcc-X':'tGravityAcc-Mean-1','tGravityAcc-Y':'tGravityAcc-Mean-2','tGravityAcc-Z':'tGravityAcc-Mean-3'}).drop(columns=['experimentID']))
               
            # tGravityAcc-STD-1              
            # tGravityAcc-STD-2              
            # tGravityAcc-STD-3     
            df_feature.append(group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].std().rename(columns={'tGravityAcc-X':'tGravityAcc-STD-1','tGravityAcc-Y':'tGravityAcc-STD-2','tGravityAcc-Z':'tGravityAcc-STD-3'}).drop(columns=['experimentID']))
    
             
            # tGravityAcc-Mad-1              
            # tGravityAcc-Mad-2              
            # tGravityAcc-Mad-3
            df_feature.append(pd.DataFrame(group['tGravityAcc-X'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tGravityAcc-X':'tGravityAcc-Mad-1'}).reset_index(drop=True)).rename(columns={0:'tGravityAcc-Mad-1'}))
            df_feature.append(pd.DataFrame(group['tGravityAcc-Y'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tGravityAcc-Y':'tGravityAcc-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tGravityAcc-Mad-2'}))
            df_feature.append(pd.DataFrame(group['tGravityAcc-Z'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tGravityAcc-Z':'tGravityAcc-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tGravityAcc-Mad-3'}))
              
            # tGravityAcc-Max-1              
            # tGravityAcc-Max-2              
            # tGravityAcc-Max-3
            df_feature.append(group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].max().rename(columns={'tGravityAcc-X':'tGravityAcc-Max-1','tGravityAcc-Y':'tGravityAcc-Max-2','tGravityAcc-Z':'tGravityAcc-Max-3'}).drop(columns=['experimentID']))
                
            # tGravityAcc-Min-1              
            # tGravityAcc-Min-2              
            # tGravityAcc-Min-3
            df_feature.append(group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].min().rename(columns={'tGravityAcc-X':'tGravityAcc-Min-1','tGravityAcc-Y':'tGravityAcc-Min-2','tGravityAcc-Z':'tGravityAcc-Min-3'}).drop(columns=['experimentID']))
            
            # tGravityAcc-SMA-1
            x=group['tGravityAcc-X'].apply(lambda x:list(x)).reset_index(drop=True)
            y=group['tGravityAcc-Y'].apply(lambda x:list(x)).reset_index(drop=True)
            z=group['tGravityAcc-Z'].apply(lambda x:list(x)).reset_index(drop=True)
            
            x=pd.DataFrame(x.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            y=pd.DataFrame(y.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            z=pd.DataFrame(z.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            
            sma=(x+y+z).rename(columns={0:'tGravityAcc-SMA-1'})
            df_feature.append(sma)

            # tGravityAcc-Energy-1           
            # tGravityAcc-Energy-2           
            # tGravityAcc-Energy-3
            a=group_square['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].sum().drop(columns=['experimentID'])
            b=group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].count().drop(columns=['experimentID'])
            df_feature.append((a/b).rename(columns={'tGravityAcc-X':'tGravityAcc-Energy-1','tGravityAcc-Y':'tGravityAcc-Energy-2','tGravityAcc-Z':'tGravityAcc-Energy-3'}))
              
            # tGravityAcc-IQR-1              
            # tGravityAcc-IQR-2              
            # tGravityAcc-IQR-3
            a=group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].quantile(0.75).reset_index(drop=True)
            b=group['tGravityAcc-X','tGravityAcc-Y','tGravityAcc-Z'].quantile(0.25).reset_index(drop=True)
            df_feature.append((a-b).rename(columns={'tGravityAcc-X':'tGravityAcc-IQR-1','tGravityAcc-Y':'tGravityAcc-IQR-2','tGravityAcc-Z':'tGravityAcc-IQR-3'}))
        
            # tGravityAcc-ropy-1             
            # tGravityAcc-ropy-1             
            # tGravityAcc-ropy-1
            x=pd.DataFrame(group['tGravityAcc-X'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tGravityAcc-ropy-1'})
            y=pd.DataFrame(group['tGravityAcc-Y'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tGravityAcc-ropy-2'})
            z=pd.DataFrame(group['tGravityAcc-Z'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tGravityAcc-ropy-3'})
            df_feature.append(x)
            df_feature.append(y)
            df_feature.append(z)
                 
            # tGravityAcc-ARCoeff-1          
            # tGravityAcc-ARCoeff-2          
            # tGravityAcc-ARCoeff-3          
            # tGravityAcc-ARCoeff-4 
            a=group['tGravityAcc-X'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tGravityAcc-X'].count()['tGravityAcc-X']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-4'}))
             
            # tGravityAcc-ARCoeff-5          
            # tGravityAcc-ARCoeff-6          
            # tGravityAcc-ARCoeff-7          
            # tGravityAcc-ARCoeff-8  
            a=group['tGravityAcc-Y'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tGravityAcc-Y'].count()['tGravityAcc-Y']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-5'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-6'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-7'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-8'}))
            
            # tGravityAcc-ARCoeff-9          
            # tGravityAcc-ARCoeff-10         
            # tGravityAcc-ARCoeff-11         
            # tGravityAcc-ARCoeff-12         
            a=group['tGravityAcc-Z'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tGravityAcc-Z'].count()['tGravityAcc-Z']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-9'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-10'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-11'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAcc-ARCoeff-12'}))
            
            # tGravityAcc-Correlation-1      
            # tGravityAcc-Correlation-2      
            # tGravityAcc-Correlation-3
            x=pd.DataFrame(group['tGravityAcc-X'].apply(lambda x:list(x))).reset_index(drop=True)
            y=pd.DataFrame(group['tGravityAcc-Y'].apply(lambda x:list(x))).reset_index(drop=True)
            z=pd.DataFrame(group['tGravityAcc-Z'].apply(lambda x:list(x))).reset_index(drop=True)
            
            yz=pd.concat([y,z],axis=1)
            yz.columns = ['y','z']
            yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tGravityAcc-Correlation-1'}))
            
            xz=pd.concat([x,z],axis=1)
            xz.columns = ['x','z']
            xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tGravityAcc-Correlation-2'}))
    
            xy=pd.concat([x,y],axis=1)
            xy.columns = ['x','y']
            xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
            df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tGravityAcc-Correlation-3'}))
    
            print('Processing tBodyAccJerk')
            
            tBodyAccJerkX = pd.DataFrame(group['tBodyAcc-X'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyAccJerk-X'})
            tBodyAccJerkY = pd.DataFrame(group['tBodyAcc-Y'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyAccJerk-Y'})
            tBodyAccJerkZ = pd.DataFrame(group['tBodyAcc-Z'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyAccJerk-Z'})
            # Remove all cases where there is no data.
            tBodyAccJerkX = tBodyAccJerkX[tBodyAccJerkX['tBodyAccJerk-X'].map(len)>0]
            tBodyAccJerkY = tBodyAccJerkY[tBodyAccJerkY['tBodyAccJerk-Y'].map(len)>0]
            tBodyAccJerkZ = tBodyAccJerkZ[tBodyAccJerkZ['tBodyAccJerk-Z'].map(len)>0]
            
            # tBodyAccJerk-Mean-1       
            # tBodyAccJerk-Mean-2            
            # tBodyAccJerk-Mean-3
            df_feature.append(tBodyAccJerkX.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-Mean-1'}))
            df_feature.append(tBodyAccJerkY.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-Mean-2'}))
            df_feature.append(tBodyAccJerkZ.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-Mean-3'}))
        
            # tBodyAccJerk-STD-1                 
            # tBodyAccJerk-STD-2                 
            # tBodyAccJerk-STD-3                 
            df_feature.append(tBodyAccJerkX.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-STD-1'}))
            df_feature.append(tBodyAccJerkY.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-STD-2'}))
            df_feature.append(tBodyAccJerkZ.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-STD-3'}))
              
            # tBodyAccJerk-Mad-1
            # tBodyAccJerk-Mad-2                 
            # tBodyAccJerk-Mad-3
            df_feature.append(tBodyAccJerkX.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-Mad-1'}))
            df_feature.append(tBodyAccJerkY.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-Mad-2'}))
            df_feature.append(tBodyAccJerkZ.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-Mad-3'}))
                  
            # tBodyAccJerk-Max-1
            # tBodyAccJerk-Max-2                 
            # tBodyAccJerk-Max-3
            df_feature.append(tBodyAccJerkX.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-Max-1'}))
            df_feature.append(tBodyAccJerkY.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-Max-2'}))
            df_feature.append(tBodyAccJerkZ.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-Max-3'}))
            
            # tBodyAccJerk-Min-1                 
            # tBodyAccJerk-Min-2                 
            # tBodyAccJerk-Min-3                 
            df_feature.append(tBodyAccJerkX.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-Min-1'}))
            df_feature.append(tBodyAccJerkY.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-Min-2'}))
            df_feature.append(tBodyAccJerkZ.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-Min-3'}))
    
            # tBodyAccJerk-SMA-1
            x=tBodyAccJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
            y=tBodyAccJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
            z=tBodyAccJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
            sma=(x+y+z).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-SMA-1'})
            df_feature.append(sma)
              
            # tBodyAccJerk-Energy-1          
            # tBodyAccJerk-Energy-2          
            # tBodyAccJerk-Energy-3 
            x=(tBodyAccJerkX**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-Energy-1'})
            y=(tBodyAccJerkY**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-Energy-2'})
            z=(tBodyAccJerkZ**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-Energy-3'})
            df_feature.append(x)
            df_feature.append(y)
            df_feature.append(z)
            
            # tBodyAccJerk-IQR-1             
            # tBodyAccJerk-IQR-2             
            # tBodyAccJerk-IQR-3
            x=pd.DataFrame(tBodyAccJerkX['tBodyAccJerk-X'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-IQR-1'})
            y=pd.DataFrame(tBodyAccJerkY['tBodyAccJerk-Y'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-IQR-2'})
            z=pd.DataFrame(tBodyAccJerkZ['tBodyAccJerk-Z'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-IQR-3'})
            df_feature.append(x)
            df_feature.append(y)
            df_feature.append(z)
               
            # tBodyAccJerk-ropy-1            
            # tBodyAccJerk-ropy-2            
            # tBodyAccJerk-ropy-3
            x=pd.DataFrame(tBodyAccJerkX['tBodyAccJerk-X'].apply(lambda x: entropy(x))).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ropy-1'})
            y=pd.DataFrame(tBodyAccJerkY['tBodyAccJerk-Y'].apply(lambda x: entropy(x))).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ropy-2'})
            z=pd.DataFrame(tBodyAccJerkZ['tBodyAccJerk-Z'].apply(lambda x: entropy(x))).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ropy-3'})
            df_feature.append(x)
            df_feature.append(y)
            df_feature.append(z)
             
            # tBodyAccJerk-ARCoeff-1         
            # tBodyAccJerk-ARCoeff-2         
            # tBodyAccJerk-ARCoeff-3         
            # tBodyAccJerk-ARCoeff-4
            mask=tBodyAccJerkX.apply(lambda lst: [len(x) for x in lst])>3
            # This will just return NaN values for too small of sample sizes
            valid=tBodyAccJerkX[mask].dropna()
            c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-X':'tBodyAccJerk-ARCoeff-4'}))
            
            # tBodyAccJerk-ARCoeff-5         
            # tBodyAccJerk-ARCoeff-6         
            # tBodyAccJerk-ARCoeff-7         
            # tBodyAccJerk-ARCoeff-8
            mask=tBodyAccJerkY.apply(lambda lst: [len(x) for x in lst])>3
            # This will just return NaN values for too small of sample sizes
            valid=tBodyAccJerkY[mask].dropna()
            c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ARCoeff-5'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ARCoeff-6'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ARCoeff-7'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Y':'tBodyAccJerk-ARCoeff-8'}))
            
            # tBodyAccJerk-ARCoeff-9         
            # tBodyAccJerk-ARCoeff-10        
            # tBodyAccJerk-ARCoeff-11        
            # tBodyAccJerk-ARCoeff-12        
            mask=tBodyAccJerkZ.apply(lambda lst: [len(x) for x in lst])>3
            # This will just return NaN values for too small of sample sizes
            valid=tBodyAccJerkZ[mask].dropna()
            c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ARCoeff-9'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ARCoeff-10'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ARCoeff-11'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerk-Z':'tBodyAccJerk-ARCoeff-12'}))
    
            # tBodyAccJerk-Correlation-1     
            # tBodyAccJerk-Correlation-2     
            # tBodyAccJerk-Correlation-3
            x=tBodyAccJerkX
            y=tBodyAccJerkY
            z=tBodyAccJerkZ
            
            yz=pd.concat([y,z],axis=1)
            yz.columns = ['y','z']
            yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tBodyAccJerk-Correlation-1'}))
            
            xz=pd.concat([x,z],axis=1)
            xz.columns = ['x','z']
            xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tBodyAccJerk-Correlation-2'}))
    
            xy=pd.concat([x,y],axis=1)
            xy.columns = ['x','y']
            xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
            df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tBodyAccJerk-Correlation-3'}))
    
            print('Processing tBodyGyro')
            
            # tBodyGyro-Mean-1
            # tBodyGyro-Mean-2                
            # tBodyGyro-Mean-3
            df_feature.append(group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].mean().rename(columns={'tBodyGyro-X':'tBodyGyro-Mean-1','tBodyGyro-Y':'tBodyGyro-Mean-2','tBodyGyro-Z':'tBodyGyro-Mean-3'}).drop(columns=['experimentID']))
    
            # tBodyGyro-STD-1                 
            # tBodyGyro-STD-2                 
            # tBodyGyro-STD-3                 
            df_feature.append(group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].std().rename(columns={'tBodyGyro-X':'tBodyGyro-STD-1','tBodyGyro-Y':'tBodyGyro-STD-2','tBodyGyro-Z':'tBodyGyro-STD-3'}).drop(columns=['experimentID']))
              
            # tBodyGyro-Mad-1
            # tBodyGyro-Mad-2                 
            # tBodyGyro-Mad-3                 
            df_feature.append(pd.DataFrame(group['tBodyGyro-X'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyGyro-X':'tBodyGyro-Mad-1'}).reset_index(drop=True)).rename(columns={0:'tBodyGyro-Mad-1'}))
            df_feature.append(pd.DataFrame(group['tBodyGyro-Y'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyGyro-Y':'tBodyGyro-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tBodyGyro-Mad-2'}))
            df_feature.append(pd.DataFrame(group['tBodyGyro-Z'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyGyro-Z':'tBodyGyro-Mad-2'}).reset_index(drop=True)).rename(columns={0:'tBodyGyro-Mad-3'}))
    
            # tBodyGyro-Max-1
            # tBodyGyro-Max-2                 
            # tBodyGyro-Max-3                 
            df_feature.append(group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].max().rename(columns={'tBodyGyro-X':'tBodyGyro-Max-1','tBodyGyro-Y':'tBodyGyro-Max-2','tBodyGyro-Z':'tBodyGyro-Max-3'}).drop(columns=['experimentID']))
    
            # tBodyGyro-Min-1                 
            # tBodyGyro-Min-2                 
            # tBodyGyro-Min-3                 
            df_feature.append(group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].min().rename(columns={'tBodyGyro-X':'tBodyGyro-Min-1','tBodyGyro-Y':'tBodyGyro-Min-2','tBodyGyro-Z':'tBodyGyro-Min-3'}).drop(columns=['experimentID']))
            
            # tBodyGyro-SMA-1
            x=group['tBodyGyro-X'].apply(lambda x:list(x)).reset_index(drop=True)
            y=group['tBodyGyro-Y'].apply(lambda x:list(x)).reset_index(drop=True)
            z=group['tBodyGyro-Z'].apply(lambda x:list(x)).reset_index(drop=True)
            
            x=pd.DataFrame(x.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            y=pd.DataFrame(y.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            z=pd.DataFrame(z.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            
            sma=(x+y+z).rename(columns={0:'tBodyGyro-SMA-1'})
            df_feature.append(sma)
            
            # tBodyGyro-Energy-1
            # tBodyGyro-Energy-2              
            # tBodyGyro-Energy-3
            a=group_square['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].sum().drop(columns=['experimentID'])
            b=group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].count().drop(columns=['experimentID'])
            df_feature.append((a/b).rename(columns={'tBodyGyro-X':'tBodyGyro-Energy-1','tBodyGyro-Y':'tBodyGyro-Energy-2','tBodyGyro-Z':'tBodyGyro-Energy-3'}))
            
            # tBodyGyro-IQR-1         
            # tBodyGyro-IQR-2                 
            # tBodyGyro-IQR-3      
            a=group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].quantile(0.75).reset_index(drop=True)
            b=group['tBodyGyro-X','tBodyGyro-Y','tBodyGyro-Z'].quantile(0.25).reset_index(drop=True)
            df_feature.append((a-b).rename(columns={'tBodyGyro-X':'tBodyGyro-IQR-1','tBodyGyro-Y':'tBodyGyro-IQR-2','tBodyGyro-Z':'tBodyGyro-IQR-3'}))
            
            # tBodyGyro-ropy-1                
            # tBodyGyro-ropy-1                
            # tBodyGyro-ropy-1   
            x=pd.DataFrame(group['tBodyGyro-X'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyGyro-ropy-1'})
            y=pd.DataFrame(group['tBodyGyro-Y'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyGyro-ropy-2'})
            z=pd.DataFrame(group['tBodyGyro-Z'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyGyro-ropy-3'})
            df_feature.append(x)
            df_feature.append(y)
            df_feature.append(z)
    
            # tBodyGyro-ARCoeff-1             
            # tBodyGyro-ARCoeff-2             
            # tBodyGyro-ARCoeff-3             
            # tBodyGyro-ARCoeff-4    
            a=group['tBodyGyro-X'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tBodyGyro-X'].count()['tBodyGyro-X']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-4'}))
            
            # tBodyGyro-ARCoeff-5             
            # tBodyGyro-ARCoeff-6             
            # tBodyGyro-ARCoeff-7             
            # tBodyGyro-ARCoeff-8
            a=group['tBodyGyro-Y'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tBodyGyro-Y'].count()['tBodyGyro-Y']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-5'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-6'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-7'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-8'}))        
    
            # tBodyGyro-ARCoeff-9             
            # tBodyGyro-ARCoeff-10            
            # tBodyGyro-ARCoeff-11            
            # tBodyGyro-ARCoeff-12
            a=group['tBodyGyro-Z'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tBodyGyro-Z'].count()['tBodyGyro-Z']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-9'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-10'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-11'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyro-ARCoeff-12'}))
            
            # tBodyGyro-Correlation-1         
            # tBodyGyro-Correlation-2         
            # tBodyGyro-Correlation-3
            x=pd.DataFrame(group['tBodyGyro-X'].apply(lambda x:list(x))).reset_index(drop=True)
            y=pd.DataFrame(group['tBodyGyro-Y'].apply(lambda x:list(x))).reset_index(drop=True)
            z=pd.DataFrame(group['tBodyGyro-Z'].apply(lambda x:list(x))).reset_index(drop=True)
            
            yz=pd.concat([y,z],axis=1)
            yz.columns = ['y','z']
            yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tBodyGyro-Correlation-1'}))
            
            xz=pd.concat([x,z],axis=1)
            xz.columns = ['x','z']
            xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tBodyGyro-Correlation-2'}))
    
            xy=pd.concat([x,y],axis=1)
            xy.columns = ['x','y']
            xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
            df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tBodyGyro-Correlation-3'}))      
        
            print('Processing tBodyGyroJerk')
         
            tBodyGyroJerkX = pd.DataFrame(group['tBodyGyro-X'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyGyroJerk-X'})
            tBodyGyroJerkY = pd.DataFrame(group['tBodyGyro-Y'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyGyroJerk-Y'})
            tBodyGyroJerkZ = pd.DataFrame(group['tBodyGyro-Z'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyGyroJerk-Z'})
            # Remove all cases where there is no data.
            tBodyGyroJerkX = tBodyGyroJerkX[tBodyGyroJerkX['tBodyGyroJerk-X'].map(len)>0]
            tBodyGyroJerkY = tBodyGyroJerkY[tBodyGyroJerkY['tBodyGyroJerk-Y'].map(len)>0]
            tBodyGyroJerkZ = tBodyGyroJerkZ[tBodyGyroJerkZ['tBodyGyroJerk-Z'].map(len)>0]
            
            # tBodyGyroJerk-Mean-1       
            # tBodyGyroJerk-Mean-2            
            # tBodyGyroJerk-Mean-3
            df_feature.append(tBodyGyroJerkX.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-Mean-1'}))
            df_feature.append(tBodyGyroJerkY.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-Mean-2'}))
            df_feature.append(tBodyGyroJerkZ.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-Mean-3'}))
        
            # tBodyGyroJerk-STD-1                 
            # tBodyGyroJerk-STD-2                 
            # tBodyGyroJerk-STD-3                 
            df_feature.append(tBodyGyroJerkX.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-STD-1'}))
            df_feature.append(tBodyGyroJerkY.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-STD-2'}))
            df_feature.append(tBodyGyroJerkZ.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-STD-3'}))
              
            # tBodyGyroJerk-Mad-1
            # tBodyGyroJerk-Mad-2                 
            # tBodyGyroJerk-Mad-3
            df_feature.append(tBodyGyroJerkX.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-Mad-1'}))
            df_feature.append(tBodyGyroJerkY.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-Mad-2'}))
            df_feature.append(tBodyGyroJerkZ.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-Mad-3'}))
                  
            # tBodyGyroJerk-Max-1
            # tBodyGyroJerk-Max-2                 
            # tBodyGyroJerk-Max-3
            df_feature.append(tBodyGyroJerkX.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-Max-1'}))
            df_feature.append(tBodyGyroJerkY.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-Max-2'}))
            df_feature.append(tBodyGyroJerkZ.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-Max-3'}))
            
            # tBodyGyroJerk-Min-1                 
            # tBodyGyroJerk-Min-2                 
            # tBodyGyroJerk-Min-3                 
            df_feature.append(tBodyGyroJerkX.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-Min-1'}))
            df_feature.append(tBodyGyroJerkY.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-Min-2'}))
            df_feature.append(tBodyGyroJerkZ.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-Min-3'}))
    
            # tBodyGyroJerk-SMA-1
            x=tBodyGyroJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
            y=tBodyGyroJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
            z=tBodyGyroJerkX.apply(lambda lst: [sum(abs(x)) for x in lst])
            sma=(x+y+z).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-SMA-1'})
            df_feature.append(sma)
              
            # tBodyGyroJerk-Energy-1          
            # tBodyGyroJerk-Energy-2          
            # tBodyGyroJerk-Energy-3 
            x=(tBodyGyroJerkX**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-Energy-1'})
            y=(tBodyGyroJerkY**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-Energy-2'})
            z=(tBodyGyroJerkZ**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-Energy-3'})
            df_feature.append(x)
            df_feature.append(y)
            df_feature.append(z)
            
            # tBodyGyroJerk-IQR-1             
            # tBodyGyroJerk-IQR-2             
            # tBodyGyroJerk-IQR-3
            x=pd.DataFrame(tBodyGyroJerkX['tBodyGyroJerk-X'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-IQR-1'})
            y=pd.DataFrame(tBodyGyroJerkY['tBodyGyroJerk-Y'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-IQR-2'})
            z=pd.DataFrame(tBodyGyroJerkZ['tBodyGyroJerk-Z'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-IQR-3'})
            df_feature.append(x)
            df_feature.append(y)
            df_feature.append(z)
               
            # tBodyGyroJerk-ropy-1            
            # tBodyGyroJerk-ropy-2            
            # tBodyGyroJerk-ropy-3
            x=pd.DataFrame(tBodyGyroJerkX['tBodyGyroJerk-X'].apply(lambda x: entropy(x))).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ropy-1'})
            y=pd.DataFrame(tBodyGyroJerkY['tBodyGyroJerk-Y'].apply(lambda x: entropy(x))).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ropy-2'})
            z=pd.DataFrame(tBodyGyroJerkZ['tBodyGyroJerk-Z'].apply(lambda x: entropy(x))).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ropy-3'})
            df_feature.append(x)
            df_feature.append(y)
            df_feature.append(z)
             
            # tBodyGyroJerk-ARCoeff-1         
            # tBodyGyroJerk-ARCoeff-2         
            # tBodyGyroJerk-ARCoeff-3         
            # tBodyGyroJerk-ARCoeff-4
            mask=tBodyGyroJerkX.apply(lambda lst: [len(x) for x in lst])>3
            # This will just return NaN values for too small of sample sizes
            valid=tBodyGyroJerkX[mask].dropna()
            c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-X':'tBodyGyroJerk-ARCoeff-4'}))
            
            # tBodyGyroJerk-ARCoeff-5         
            # tBodyGyroJerk-ARCoeff-6         
            # tBodyGyroJerk-ARCoeff-7         
            # tBodyGyroJerk-ARCoeff-8
            mask=tBodyGyroJerkY.apply(lambda lst: [len(x) for x in lst])>3
            # This will just return NaN values for too small of sample sizes
            valid=tBodyGyroJerkY[mask].dropna()
            c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ARCoeff-5'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ARCoeff-6'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ARCoeff-7'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Y':'tBodyGyroJerk-ARCoeff-8'}))
            
            # tBodyGyroJerk-ARCoeff-9         
            # tBodyGyroJerk-ARCoeff-10        
            # tBodyGyroJerk-ARCoeff-11        
            # tBodyGyroJerk-ARCoeff-12        
            mask=tBodyGyroJerkZ.apply(lambda lst: [len(x) for x in lst])>3
            # This will just return NaN values for too small of sample sizes
            valid=tBodyGyroJerkZ[mask].dropna()
            c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ARCoeff-9'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ARCoeff-10'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ARCoeff-11'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerk-Z':'tBodyGyroJerk-ARCoeff-12'}))
    
            # tBodyGyroJerk-Correlation-1     
            # tBodyGyroJerk-Correlation-2     
            # tBodyGyroJerk-Correlation-3
            x=tBodyGyroJerkX
            y=tBodyGyroJerkY
            z=tBodyGyroJerkZ
            
            yz=pd.concat([y,z],axis=1)
            yz.columns = ['y','z']
            yz=yz.apply(lambda row: pearsonr(row['y'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(yz.apply(lambda x: x[0])).rename(columns={0:'tBodyGyroJerk-Correlation-1'}))
            
            xz=pd.concat([x,z],axis=1)
            xz.columns = ['x','z']
            xz=xz.apply(lambda row: pearsonr(row['x'],row['z']), axis=1)
            df_feature.append(pd.DataFrame(xz.apply(lambda x: x[0])).rename(columns={0:'tBodyGyroJerk-Correlation-2'}))
    
            xy=pd.concat([x,y],axis=1)
            xy.columns = ['x','y']
            xy=xy.apply(lambda row: pearsonr(row['x'],row['y']), axis=1)
            df_feature.append(pd.DataFrame(xy.apply(lambda x: x[0])).rename(columns={0:'tBodyGyroJerk-Correlation-3'}))
    
            print('Processing tBodyAccMag')        
    
            # tBodyAccMag-Mean-1        
            df_feature.append(group['tBodyAccMag'].mean().rename(columns={'tBodyAccMag':'tBodyAccMag-Mean-1'}).drop(columns=['experimentID']))
            
            # tBodyAccMag-STD-1              
            df_feature.append(group['tBodyAccMag'].std().rename(columns={'tBodyAccMag':'tBodyAccMag-STD-1'}).drop(columns=['experimentID']))
    
            # tBodyAccMag-Mad-1              
            df_feature.append(pd.DataFrame(group['tBodyAccMag'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyAcc':'tBodyAccMag-Mad-1'}).reset_index(drop=True)).rename(columns={0:'tBodyAccMag-Mad-1'}))
    
            # tBodyAccMag-Max-1              
            df_feature.append(group['tBodyAccMag'].max().rename(columns={'tBodyAccMag':'tBodyAccMag-Max-1'}).drop(columns=['experimentID']))
    
            # tBodyAccMag-Min-1              
            df_feature.append(group['tBodyAccMag'].min().rename(columns={'tBodyAccMag':'tBodyAccMag-Min-1'}).drop(columns=['experimentID']))
    
            # tBodyAccMag-SMA-1              
            x=group['tBodyAccMag'].apply(lambda x:list(x)).reset_index(drop=True)
            x=pd.DataFrame(x.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            sma=(x).rename(columns={0:'tBodyAccMag-SMA-1'})
            df_feature.append(sma)
       
            # tBodyAccMag-Energy-1
            a=group_square['tBodyAccMag'].sum().drop(columns=['experimentID'])
            b=group['tBodyAccMag'].count().drop(columns=['experimentID'])
            df_feature.append((a/b).rename(columns={'tBodyAccMag':'tBodyAccMag-Energy-1'}))
    
            # tBodyAccMag-IQR-1              
            a=group['tBodyAccMag'].quantile(0.75).reset_index(drop=True)
            b=group['tBodyAccMag'].quantile(0.25).reset_index(drop=True)
            df_feature.append(pd.DataFrame((a-b)).rename(columns={0:'tBodyAccMag-IQR-1'}))
    
            # tBodyAccMag-ropy-1      
            x=pd.DataFrame(group['tBodyAccMag'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyAccMag-ropy-1'})
            df_feature.append(x)
          
            # tBodyAccMag-ARCoeff-1          
            # tBodyAccMag-ARCoeff-2          
            # tBodyAccMag-ARCoeff-3          
            # tBodyAccMag-ARCoeff-4     
            a=group['tBodyAccMag'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tBodyAccMag'].count()['tBodyAccMag']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAccMag-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAccMag-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAccMag-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyAccMag-ARCoeff-4'}))
            
            print('Processing tGravityAccMag')
            
            # tGravityAccMag-Mean-1        
            df_feature.append(group['tGravityAccMag'].mean().rename(columns={'tGravityAccMag':'tGravityAccMag-Mean-1'}).drop(columns=['experimentID']))
            
            # tGravityAccMag-STD-1              
            df_feature.append(group['tGravityAccMag'].std().rename(columns={'tGravityAccMag':'tGravityAccMag-STD-1'}).drop(columns=['experimentID']))
    
            # tGravityAccMag-Mad-1              
            df_feature.append(pd.DataFrame(group['tGravityAccMag'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyAcc':'tGravityAccMag-Mad-1'}).reset_index(drop=True)).rename(columns={0:'tGravityAccMag-Mad-1'}))
    
            # tGravityAccMag-Max-1              
            df_feature.append(group['tGravityAccMag'].max().rename(columns={'tGravityAccMag':'tGravityAccMag-Max-1'}).drop(columns=['experimentID']))
    
            # tGravityAccMag-Min-1              
            df_feature.append(group['tGravityAccMag'].min().rename(columns={'tGravityAccMag':'tGravityAccMag-Min-1'}).drop(columns=['experimentID']))
    
            # tGravityAccMag-SMA-1              
            x=group['tGravityAccMag'].apply(lambda x:list(x)).reset_index(drop=True)
            x=pd.DataFrame(x.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            sma=(x).rename(columns={0:'tGravityAccMag-SMA-1'})
            df_feature.append(sma)
       
            # tGravityAccMag-Energy-1
            a=group_square['tGravityAccMag'].sum().drop(columns=['experimentID'])
            b=group['tGravityAccMag'].count().drop(columns=['experimentID'])
            df_feature.append((a/b).rename(columns={'tGravityAccMag':'tGravityAccMag-Energy-1'}))
    
            # tGravityAccMag-IQR-1              
            a=group['tGravityAccMag'].quantile(0.75).reset_index(drop=True)
            b=group['tGravityAccMag'].quantile(0.25).reset_index(drop=True)
            df_feature.append(pd.DataFrame((a-b)).rename(columns={0:'tGravityAccMag-IQR-1'}))
    
            # tGravityAccMag-ropy-1      
            x=pd.DataFrame(group['tGravityAccMag'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tGravityAccMag-ropy-1'})
            df_feature.append(x)
          
            # tGravityAccMag-ARCoeff-1          
            # tGravityAccMag-ARCoeff-2          
            # tGravityAccMag-ARCoeff-3          
            # tGravityAccMag-ARCoeff-4     
            a=group['tGravityAccMag'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tGravityAccMag'].count()['tGravityAccMag']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAccMag-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAccMag-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAccMag-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tGravityAccMag-ARCoeff-4'}))
            
            print('Processing tBodyAccJerkMag')    
            
            tBodyAccJerkMag = pd.DataFrame(group['tBodyAccMag'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyAccJerkMag'})
            tBodyAccJerkMag = tBodyAccJerkMag[tBodyAccJerkMag['tBodyAccJerkMag'].map(len)>0]
    
            # tBodyAccJerkMag-Mean-1       
            df_feature.append(tBodyAccJerkMag.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-Mean-1'}))
        
            # tBodyAccJerkMag-STD-1                 
            df_feature.append(tBodyAccJerkMag.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-STD-1'}))
              
            # tBodyAccJerkMag-Mad-1
            df_feature.append(tBodyAccJerkMag.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-Mad-1'}))
                  
            # tBodyAccJerkMag-Max-1
            df_feature.append(tBodyAccJerkMag.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-Max-1'}))
            
            # tBodyAccJerkMag-Min-1                 
            df_feature.append(tBodyAccJerkMag.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-Min-1'}))
    
            # tBodyAccJerkMag-SMA-1
            x=tBodyAccJerkMag.apply(lambda lst: [sum(abs(x)) for x in lst])
            sma=(x).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-SMA-1'})
            df_feature.append(sma)
              
            # tBodyAccJerkMag-Energy-1          
            x=(tBodyAccJerkMag**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-Energy-1'})
            df_feature.append(x)
            
            # tBodyAccJerkMag-IQR-1             
            x=pd.DataFrame(tBodyAccJerkMag['tBodyAccJerkMag'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-IQR-1'})
            df_feature.append(x)
               
            # tBodyAccJerkMag-ropy-1            
            x=pd.DataFrame(tBodyAccJerkMag['tBodyAccJerkMag'].apply(lambda x: entropy(x))).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-ropy-1'})
            df_feature.append(x)
             
            # tBodyAccJerkMag-ARCoeff-1   
            # tBodyAccJerkMag-ARCoeff-2         
            # tBodyAccJerkMag-ARCoeff-3         
            # tBodyAccJerkMag-ARCoeff-4
            mask=tBodyAccJerkMag.apply(lambda lst: [len(x) for x in lst])>3
            valid=tBodyAccJerkMag[mask].dropna()
            c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyAccJerkMag':'tBodyAccJerkMag-ARCoeff-4'}))
            
            print('Processing tBodyGyroMag')
    
            # tBodyGyroMag-Mean-1   
            df_feature.append(group['tBodyGyroMag'].mean().rename(columns={'tBodyGyroMag':'tBodyGyroMag-Mean-1'}).drop(columns=['experimentID']))
            
            # tBodyGyroMag-STD-1           
            df_feature.append(group['tBodyGyroMag'].std().rename(columns={'tBodyGyroMag':'tBodyGyroMag-STD-1'}).drop(columns=['experimentID']))
    
            # tBodyGyroMag-Mad-1         
            df_feature.append(pd.DataFrame(group['tBodyGyroMag'].apply(lambda x: median_absolute_deviation(x)).rename(columns={'tBodyAcc':'tBodyGyroMag-Mad-1'}).reset_index(drop=True)).rename(columns={0:'tBodyGyroMag-Mad-1'}))
    
            # tBodyGyroMag-Max-1           
            df_feature.append(group['tBodyGyroMag'].max().rename(columns={'tBodyGyroMag':'tBodyGyroMag-Max-1'}).drop(columns=['experimentID']))
    
            # tBodyGyroMag-Min-1        
            df_feature.append(group['tBodyGyroMag'].min().rename(columns={'tBodyGyroMag':'tBodyGyroMag-Min-1'}).drop(columns=['experimentID']))
    
            # tBodyGyroMag-SMA-1              
            x=group['tBodyGyroMag'].apply(lambda x:list(x)).reset_index(drop=True)
            x=pd.DataFrame(x.apply(lambda lst: [abs(x) for x in lst]).apply(lambda x: sum(x)))
            sma=(x).rename(columns={0:'tBodyGyroMag-SMA-1'})
            df_feature.append(sma)
       
            # tBodyGyroMag-Energy-1
            a=group_square['tBodyGyroMag'].sum().drop(columns=['experimentID'])
            b=group['tBodyGyroMag'].count().drop(columns=['experimentID'])
            df_feature.append((a/b).rename(columns={'tBodyGyroMag':'tBodyGyroMag-Energy-1'}))
    
            # tBodyGyroMag-IQR-1              
            a=group['tBodyGyroMag'].quantile(0.75).reset_index(drop=True)
            b=group['tBodyGyroMag'].quantile(0.25).reset_index(drop=True)
            df_feature.append(pd.DataFrame((a-b)).rename(columns={0:'tBodyGyroMag-IQR-1'}))
    
            # tBodyGyroMag-ropy-1      
            x=pd.DataFrame(group['tBodyGyroMag'].apply(entropy).reset_index(drop=True)).rename(columns={0:'tBodyGyroMag-ropy-1'})
            df_feature.append(x)
          
            # tBodyGyroMag-ARCoeff-1          
            # tBodyGyroMag-ARCoeff-2          
            # tBodyGyroMag-ARCoeff-3          
            # tBodyGyroMag-ARCoeff-4     
            a=group['tBodyGyroMag'].apply(lambda x: list(x)).drop(columns='experimentID').reset_index(drop=True)
            b=pd.DataFrame(a)
            mask=(group['tBodyGyroMag'].count()['tBodyGyroMag']>3).values.tolist()
            b_valid = b[mask]
            c=b_valid[0].apply(lambda x: _arburg2(x,4))
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyroMag-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyroMag-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyroMag-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={0:'tBodyGyroMag-ARCoeff-4'})) 
        
            print('Processing tBodyGyroJerkMag')      
    
            tBodyGyroJerkMag = pd.DataFrame(group['tBodyGyroMag'].apply(lambda x: list(x)).apply(lambda row: np.diff(row)/(1/hz)).reset_index(drop=True)).rename(columns={0:'tBodyGyroJerkMag'})
            tBodyGyroJerkMag = tBodyGyroJerkMag[tBodyGyroJerkMag['tBodyGyroJerkMag'].map(len)>0]
    
            # tBodyGyroJerkMag-Mean-1       
            df_feature.append(tBodyGyroJerkMag.apply(lambda row: [np.mean(y) for y in row]).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-Mean-1'}))
        
            # tBodyGyroJerkMag-STD-1                 
            df_feature.append(tBodyGyroJerkMag.apply(lambda row: [np.std(y) for y in row]).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-STD-1'}))
              
            # tBodyGyroJerkMag-Mad-1
            df_feature.append(tBodyGyroJerkMag.apply(lambda row: [mad2(y) for y in row]).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-Mad-1'}))
                  
            # tBodyGyroJerkMag-Max-1
            df_feature.append(tBodyGyroJerkMag.apply(lambda x: [np.sort(y)[-1:].sum() for y in x]).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-Max-1'}))
            
            # tBodyGyroJerkMag-Min-1                 
            df_feature.append(tBodyGyroJerkMag.apply(lambda x: [np.sort(y)[:1].sum() for y in x]).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-Min-1'}))
    
            # tBodyGyroJerkMag-SMA-1
            x=tBodyGyroJerkMag.apply(lambda lst: [sum(abs(x)) for x in lst])
            sma=(x).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-SMA-1'})
            df_feature.append(sma)
              
            # tBodyGyroJerkMag-Energy-1          
            x=(tBodyGyroJerkMag**2).apply(lambda lst: [sum(x)/len(x) for x in lst]).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-Energy-1'})
            df_feature.append(x)
            
            # tBodyGyroJerkMag-IQR-1             
            x=pd.DataFrame(tBodyGyroJerkMag['tBodyGyroJerkMag'].apply(lambda x: np.percentile(x,75)-np.percentile(x,25))).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-IQR-1'})
            df_feature.append(x)
               
            # tBodyGyroJerkMag-ropy-1            
            x=pd.DataFrame(tBodyGyroJerkMag['tBodyGyroJerkMag'].apply(lambda x: entropy(x))).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-ropy-1'})
            df_feature.append(x)
             
            # tBodyGyroJerkMag-ARCoeff-1         
            # tBodyGyroJerkMag-ARCoeff-2         
            # tBodyGyroJerkMag-ARCoeff-3         
            # tBodyGyroJerkMag-ARCoeff-4
            mask=tBodyGyroJerkMag.apply(lambda lst: [len(x) for x in lst])>3
            valid=tBodyGyroJerkMag[mask].dropna()
            c=valid.apply(lambda lst: [_arburg2(x,4) for x in lst])
            d = pd.DataFrame(c)
            e=d.apply(lambda x: [y[0] for y in list(x)])
            df_feature.append(e.apply(lambda x: [y[1] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-ARCoeff-1'}))
            df_feature.append(e.apply(lambda x: [y[2] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-ARCoeff-2'}))
            df_feature.append(e.apply(lambda x: [y[3] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-ARCoeff-3'}))
            df_feature.append(e.apply(lambda x: [y[4] for y in list(x)]).apply(lambda x: x.real).rename(columns={'tBodyGyroJerkMag':'tBodyGyroJerkMag-ARCoeff-4'}))      
            
            print('Processing f-transformed')
            # FFT applied with real values only as output
            
            df_f = pd.DataFrame()
            
            # Calculate FFT of each raw column
            df_f['fBodyAcc-X'] = group['tBodyAcc-X'].apply(lambda x: np.absolute(np.fft.rfft(x))).reset_index()['tBodyAcc-X']
            df_f['fBodyAcc-Y'] = group['tBodyAcc-Y'].apply(lambda x: np.absolute(np.fft.rfft(x))).reset_index()['tBodyAcc-Y']
            df_f['fBodyAcc-Z'] = group['tBodyAcc-Z'].apply(lambda x: np.absolute(np.fft.rfft(x))).reset_index()['tBodyAcc-Z']
            
            df_f['fBodyAccJerk-X'] = tBodyAccJerkX.apply(lambda row: [np.absolute(np.fft.rfft(y)) for y in row]).rename(columns={'tBodyAccJerk-X':'fBodyAccJerk-X'})
            df_f['fBodyAccJerk-Y'] = tBodyAccJerkY.apply(lambda row: [np.absolute(np.fft.rfft(y)) for y in row]).rename(columns={'tBodyAccJerk-Y':'fBodyAccJerk-Y'})
            df_f['fBodyAccJerk-Z'] = tBodyAccJerkZ.apply(lambda row: [np.absolute(np.fft.rfft(y)) for y in row]).rename(columns={'tBodyAccJerk-Z':'fBodyAccJerk-Z'})
            
            df_f['fBodyGyro-X'] = group['tBodyGyro-X'].apply(lambda x: np.absolute(np.fft.rfft(x))).reset_index()['tBodyGyro-X']
            df_f['fBodyGyro-Y'] = group['tBodyGyro-Y'].apply(lambda x: np.absolute(np.fft.rfft(x))).reset_index()['tBodyGyro-Y']
            df_f['fBodyGyro-Z'] = group['tBodyGyro-Z'].apply(lambda x: np.absolute(np.fft.rfft(x))).reset_index()['tBodyGyro-Z']
    
            df_f['fBodyGyroJerk-X'] = tBodyGyroJerkX.apply(lambda row: [np.absolute(np.fft.rfft(y)) for y in row]).rename(columns={'tBodyGyroJerk-X':'fBodyGyroJerk-X'})
            df_f['fBodyGyroJerk-Y'] = tBodyGyroJerkY.apply(lambda row: [np.absolute(np.fft.rfft(y)) for y in row]).rename(columns={'tBodyGyroJerk-Y':'fBodyGyroJerk-Y'})
            df_f['fBodyGyroJerk-Z'] = tBodyGyroJerkZ.apply(lambda row: [np.absolute(np.fft.rfft(y)) for y in row]).rename(columns={'tBodyGyroJerk-Z':'fBodyGyroJerk-Z'})
    
            t = np.square(df_f[['fBodyAcc-X','fBodyAcc-Y','fBodyAcc-Z']])
            t = t['fBodyAcc-X']+t['fBodyAcc-Y']+t['fBodyAcc-Z']
            t = t.apply(lambda row: np.sqrt(row))
            df_f['fBodyAccMag'] = pd.DataFrame(t).rename(columns={0:'fBodyAccMag'})
            
            t = np.square(df_f[['fBodyGyro-X','fBodyGyro-Y','fBodyGyro-Z']])
            t = t['fBodyGyro-X']+t['fBodyGyro-Y']+t['fBodyGyro-Z']
            t = t.apply(lambda row: np.sqrt(row))
            df_f['fBodyGyroMag'] = pd.DataFrame(t).rename(columns={0:'fBodyGryoMag'})
            
            t = np.square(df_f[['fBodyAccJerk-X','fBodyAccJerk-Y','fBodyAccJerk-Z']])
            t = t['fBodyAccJerk-X']+t['fBodyAccJerk-Y']+t['fBodyAccJerk-Z']
            t = t.apply(lambda row: np.sqrt(row))
            df_f['fBodyAccJerkMag'] = pd.DataFrame(t).rename(columns={0:'fBodyAccJerkMag'})
            
            t = np.square(df_f[['fBodyGyroJerk-X','fBodyGyroJerk-Y','fBodyGyroJerk-Z']])
            t = t['fBodyGyroJerk-X']+t['fBodyGyroJerk-Y']+t['fBodyGyroJerk-Z']
            t = t.apply(lambda row: np.sqrt(row))
            df_f['fBodyGyroJerkMag'] = pd.DataFrame(t).rename(columns={0:'fBodyGyroJerkMag'})   
      
            # fBodyAcc-Mean-1                
            # fBodyAcc-Mean-2                
            # fBodyAcc-Mean-3  
            df_feature.append(df_f[['fBodyAcc-X']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyAcc-X':'fBodyAcc-Mean-1'}))
            df_feature.append(df_f[['fBodyAcc-Y']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyAcc-Y':'fBodyAcc-Mean-2'}))
            df_feature.append(df_f[['fBodyAcc-Z']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyAcc-Z':'fBodyAcc-Mean-3'}))
    
            # fBodyAcc-STD-1                 
            # fBodyAcc-STD-2                 
            # fBodyAcc-STD-3
            df_feature.append(df_f[['fBodyAcc-X']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyAcc-X':'fBodyAcc-STD-1'}))
            df_feature.append(df_f[['fBodyAcc-Y']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyAcc-Y':'fBodyAcc-STD-2'}))
            df_feature.append(df_f[['fBodyAcc-Z']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyAcc-Z':'fBodyAcc-STD-3'}))
    
            # fBodyAcc-Mad-1                 
            # fBodyAcc-Mad-2                 
            # fBodyAcc-Mad-3
            df_feature.append(df_f[['fBodyAcc-X']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyAcc-X':'fBodyAcc-Mad-1'}))
            df_feature.append(df_f[['fBodyAcc-Y']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyAcc-Y':'fBodyAcc-Mad-2'}))
            df_feature.append(df_f[['fBodyAcc-Z']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyAcc-Z':'fBodyAcc-Mad-3'}))
    
            # fBodyAcc-Max-1                 
            # fBodyAcc-Max-2                 
            # fBodyAcc-Max-3                 
            df_feature.append(df_f[['fBodyAcc-X']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyAcc-X':'fBodyAcc-Max-1'}))
            df_feature.append(df_f[['fBodyAcc-Y']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyAcc-Y':'fBodyAcc-Max-2'}))
            df_feature.append(df_f[['fBodyAcc-Z']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyAcc-Z':'fBodyAcc-Max-3'}))
    
            # fBodyAcc-Min-1                 
            # fBodyAcc-Min-2                 
            # fBodyAcc-Min-3
            df_feature.append(df_f[['fBodyAcc-X']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyAcc-X':'fBodyAcc-Min-1'}))
            df_feature.append(df_f[['fBodyAcc-Y']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyAcc-Y':'fBodyAcc-Min-2'}))
            df_feature.append(df_f[['fBodyAcc-Z']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyAcc-Z':'fBodyAcc-Min-3'}))
                 
            # fBodyAcc-SMA-1
            t = df_f[['fBodyAcc-X','fBodyAcc-Y','fBodyAcc-Z']].abs().sum(axis=1)
            t = pd.DataFrame(t.apply(lambda row: sum(row))).rename(columns={0:'fBodyAcc-SMA-1'})
            df_feature.append(t)
            
            # fBodyAcc-Energy-1              
            # fBodyAcc-Energy-2              
            # fBodyAcc-Energy-3 
            t = np.square(df_f[['fBodyAcc-X']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyAcc-X':'fBodyAcc-Energy-1'})
            df_feature.append(t)
            t = np.square(df_f[['fBodyAcc-Y']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyAcc-Y':'fBodyAcc-Energy-2'})
            df_feature.append(t)
            t = np.square(df_f[['fBodyAcc-Z']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyAcc-Z':'fBodyAcc-Energy-3'})
            df_feature.append(t)
            
            # fBodyAcc-IQR-1                 
            # fBodyAcc-IQR-2                 
            # fBodyAcc-IQR-3
            x=df_f['fBodyAcc-X'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyAcc-IQR-1'})
            y=df_f['fBodyAcc-Y'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyAcc-IQR-2'})
            z=df_f['fBodyAcc-Z'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyAcc-IQR-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # fBodyAcc-ropy-1                
            # fBodyAcc-ropy-1                
            # fBodyAcc-ropy-1   
            x=pd.DataFrame(df_f['fBodyAcc-X'].apply(lambda row: entropy(row))).rename(columns={'fBodyAcc-X':'fBodyAcc-ropy-1'})
            y=pd.DataFrame(df_f['fBodyAcc-Y'].apply(lambda row: entropy(row))).rename(columns={'fBodyAcc-Y':'fBodyAcc-ropy-2'})
            z=pd.DataFrame(df_f['fBodyAcc-Z'].apply(lambda row: entropy(row))).rename(columns={'fBodyAcc-Z':'fBodyAcc-ropy-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # fBodyAcc-MaxInds-1             
            # fBodyAcc-MaxInds-2             
            # fBodyAcc-MaxInds-3
            x=pd.DataFrame(df_f['fBodyAcc-X'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyAcc-X':'fBodyAcc-MaxInds-1'})
            y=pd.DataFrame(df_f['fBodyAcc-Y'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyAcc-Y':'fBodyAcc-MaxInds-2'})
            z=pd.DataFrame(df_f['fBodyAcc-Z'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyAcc-Z':'fBodyAcc-MaxInds-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # Get frequency buckets for this sampling profile
            freqbuckets = np.fft.rfftfreq(hz*seconds, 1/hz)
            
            # fBodyAcc-MeanFreq-1            
            # fBodyAcc-MeanFreq-2            
            # fBodyAcc-MeanFreq-3 
            x=pd.DataFrame(df_f['fBodyAcc-X'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyAcc-X':'fBodyAcc-MeanFreq-1'})
            y=pd.DataFrame(df_f['fBodyAcc-Y'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyAcc-Y':'fBodyAcc-MeanFreq-2'})
            z=pd.DataFrame(df_f['fBodyAcc-Z'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyAcc-Z':'fBodyAcc-MeanFreq-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # fBodyAcc-Skewness-1            
            # fBodyAcc-Kurtosis-1            
            # fBodyAcc-Skewness-2            
            # fBodyAcc-Kurtosis-2            
            # fBodyAcc-Skewness-3            
            # fBodyAcc-Kurtosis-3
            x=pd.DataFrame(df_f['fBodyAcc-X'].apply(lambda x: skew(x))).rename(columns={'fBodyAcc-X':'fBodyAcc-Skewness-1'})
            y=pd.DataFrame(df_f['fBodyAcc-Y'].apply(lambda x: skew(x))).rename(columns={'fBodyAcc-Y':'fBodyAcc-Skewness-2'})
            z=pd.DataFrame(df_f['fBodyAcc-Z'].apply(lambda x: skew(x))).rename(columns={'fBodyAcc-Z':'fBodyAcc-Skewness-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            x=pd.DataFrame(df_f['fBodyAcc-X'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyAcc-X':'fBodyAcc-Kurtosis-1'})
            y=pd.DataFrame(df_f['fBodyAcc-Y'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyAcc-Y':'fBodyAcc-Kurtosis-2'})
            z=pd.DataFrame(df_f['fBodyAcc-Z'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyAcc-Z':'fBodyAcc-Kurtosis-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)

            # Energy of frequency bands
            
            #fBodyAcc-BandsEnergy-X-1
            #fBodyAcc-BandsEnergy-X-2
            #fBodyAcc-BandsEnergy-X-3
            #fBodyAcc-BandsEnergy-X-4
            #fBodyAcc-BandsEnergy-X-5
            #fBodyAcc-BandsEnergy-X-6 
            #fBodyAcc-BandsEnergy-X-7 
            #fBodyAcc-BandsEnergy-X-8 
            #fBodyAcc-BandsEnergy-X-9 
            #fBodyAcc-BandsEnergy-X-10
            #fBodyAcc-BandsEnergy-X-11
            #fBodyAcc-BandsEnergy-X-12
            #fBodyAcc-BandsEnergy-X-13
            #fBodyAcc-BandsEnergy-X-14
            #fBodyAcc-BandsEnergy-X-15
            #fBodyAcc-BandsEnergy-Y-1
            #fBodyAcc-BandsEnergy-Y-2
            #fBodyAcc-BandsEnergy-Y-3
            #fBodyAcc-BandsEnergy-Y-4
            #fBodyAcc-BandsEnergy-Y-5
            #fBodyAcc-BandsEnergy-Y-6 
            #fBodyAcc-BandsEnergy-Y-7 
            #fBodyAcc-BandsEnergy-Y-8 
            #fBodyAcc-BandsEnergy-Y-9 
            #fBodyAcc-BandsEnergy-Y-10
            #fBodyAcc-BandsEnergy-Y-11
            #fBodyAcc-BandsEnergy-Y-12
            #fBodyAcc-BandsEnergy-Y-13
            #fBodyAcc-BandsEnergy-Y-14
            #fBodyAcc-BandsEnergy-Y-15
            #fBodyAcc-BandsEnergy-Z-1
            #fBodyAcc-BandsEnergy-Z-2
            #fBodyAcc-BandsEnergy-Z-3
            #fBodyAcc-BandsEnergy-Z-4
            #fBodyAcc-BandsEnergy-Z-5
            #fBodyAcc-BandsEnergy-Z-6 
            #fBodyAcc-BandsEnergy-Z-7 
            #fBodyAcc-BandsEnergy-Z-8 
            #fBodyAcc-BandsEnergy-Z-9 
            #fBodyAcc-BandsEnergy-Z-10
            #fBodyAcc-BandsEnergy-Z-11
            #fBodyAcc-BandsEnergy-Z-12
            #fBodyAcc-BandsEnergy-Z-13
            #fBodyAcc-BandsEnergy-Z-14
            #fBodyAcc-BandsEnergy-Z-15
            
            '''
            Note that since num of frequency buckets = hz*seconds/2 + 1,
            each file may have a different number of bands available. Here
            we split the frequency bucket list into sqrt(len(freqbuckets)))
            separate chunks because it seems like a reasonable number, then 
            calculate the energy of each set of bands, then pad the number 
            of resulting columns with all-NA columns so that each data set
            has an equivalent number of columns (for easier future processing).
            '''
            
            maxbands = 15 # This is num of bands for 50hz, 10 seconds file
            nbands = np.sqrt(len(freqbuckets))
            if (nbands < 5):
                nbands = len(freqbuckets) # Set better minimum number of bands
            fbucketlist = np.array_split(freqbuckets, nbands)
            
            #df_feature_test = df_feature
            
            for var in ['X', 'Y', 'Z']:
                incolname = 'fBodyAcc-%s' % var
                startind = 0
                for i in np.arange(maxbands):
                    cname = "fBodyAcc-BandsEnergy-%s-%s" % (var, i+1)
                    try:
                        # If i is a valid index of fbucketlist, create column
                        band = fbucketlist[i]
                        bandinds = np.arange(startind, startind+len(band))
                        print("Creating column %s" % cname)
                        df_feature.append(pd.DataFrame(df_f[incolname].apply(lambda x: np.sqrt(sum([y**2 for y in x[bandinds]]))).rename(columns={incolname:cname}).reset_index(drop=True)).rename(columns={0:cname}))
                        startind += len(bandinds)
                    except:
                        # i is not a valid index, fill column with NAN
                        print("No more bands, filling column %s with NANs" % cname)
                        df_feature.append(pd.DataFrame(np.full((2220, 1), fill_value=np.NAN)).rename(columns={0:cname}))
                
            # fBodyAccJerk-Mean-1                
            # fBodyAccJerk-Mean-2                
            # fBodyAccJerk-Mean-3  
            df_feature.append(df_f[['fBodyAccJerk-X']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-Mean-1'}))
            df_feature.append(df_f[['fBodyAccJerk-Y']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-Mean-2'}))
            df_feature.append(df_f[['fBodyAccJerk-Z']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-Mean-3'}))
    
            # fBodyAccJerk-STD-1                 
            # fBodyAccJerk-STD-2                 
            # fBodyAccJerk-STD-3
            df_feature.append(df_f[['fBodyAccJerk-X']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-STD-1'}))
            df_feature.append(df_f[['fBodyAccJerk-Y']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-STD-2'}))
            df_feature.append(df_f[['fBodyAccJerk-Z']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-STD-3'}))
    
            # fBodyAccJerk-Mad-1                 
            # fBodyAccJerk-Mad-2                 
            # fBodyAccJerk-Mad-3
            df_feature.append(df_f[['fBodyAccJerk-X']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-Mad-1'}))
            df_feature.append(df_f[['fBodyAccJerk-Y']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-Mad-2'}))
            df_feature.append(df_f[['fBodyAccJerk-Z']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-Mad-3'}))
    
            # fBodyAccJerk-Max-1                 
            # fBodyAccJerk-Max-2                 
            # fBodyAccJerk-Max-3                 
            df_feature.append(df_f[['fBodyAccJerk-X']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-Max-1'}))
            df_feature.append(df_f[['fBodyAccJerk-Y']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-Max-2'}))
            df_feature.append(df_f[['fBodyAccJerk-Z']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-Max-3'}))
    
            # fBodyAccJerk-Min-1                 
            # fBodyAccJerk-Min-2                 
            # fBodyAccJerk-Min-3
            df_feature.append(df_f[['fBodyAccJerk-X']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-Min-1'}))
            df_feature.append(df_f[['fBodyAccJerk-Y']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-Min-2'}))
            df_feature.append(df_f[['fBodyAccJerk-Z']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-Min-3'}))
                   
            # fBodyAccJerk-SMA-1
            t = df_f[['fBodyAccJerk-X','fBodyAccJerk-Y','fBodyAccJerk-Z']].abs().sum(axis=1)
            t = pd.DataFrame(t.apply(lambda row: sum(row))).rename(columns={0:'fBodyAccJerk-SMA-1'})
            df_feature.append(t)
                   
            # fBodyAccJerk-Energy-1              
            # fBodyAccJerk-Energy-2              
            # fBodyAccJerk-Energy-3 
            t = np.square(df_f[['fBodyAccJerk-X']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-Energy-1'})
            df_feature.append(t)
            t = np.square(df_f[['fBodyAccJerk-Y']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-Energy-2'})
            df_feature.append(t)
            t = np.square(df_f[['fBodyAccJerk-Z']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-Energy-3'})
            df_feature.append(t)
            
            # fBodyAccJerk-IQR-1                 
            # fBodyAccJerk-IQR-2                 
            # fBodyAccJerk-IQR-3
            x=df_f['fBodyAccJerk-X'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyAccJerk-IQR-1'})
            y=df_f['fBodyAccJerk-Y'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyAccJerk-IQR-2'})
            z=df_f['fBodyAccJerk-Z'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyAccJerk-IQR-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # fBodyAccJerk-ropy-1                
            # fBodyAccJerk-ropy-1                
            # fBodyAccJerk-ropy-1   
            x=pd.DataFrame(df_f['fBodyAccJerk-X'].apply(lambda row: entropy(row))).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-ropy-1'})
            y=pd.DataFrame(df_f['fBodyAccJerk-Y'].apply(lambda row: entropy(row))).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-ropy-2'})
            z=pd.DataFrame(df_f['fBodyAccJerk-Z'].apply(lambda row: entropy(row))).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-ropy-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
    
            # fBodyAccJerk-MaxInds-1             
            # fBodyAccJerk-MaxInds-2             
            # fBodyAccJerk-MaxInds-3
            x=pd.DataFrame(df_f['fBodyAccJerk-X'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-MaxInds-1'})
            y=pd.DataFrame(df_f['fBodyAccJerk-Y'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-MaxInds-2'})
            z=pd.DataFrame(df_f['fBodyAccJerk-Z'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-MaxInds-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # Get frequency buckets for this sampling profile
            freqbuckets = np.fft.rfftfreq(hz*seconds, 1/hz)
            
            # fBodyAccJerk-MeanFreq-1            
            # fBodyAccJerk-MeanFreq-2            
            # fBodyAccJerk-MeanFreq-3 
            x=pd.DataFrame(df_f['fBodyAccJerk-X'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-MeanFreq-1'})
            y=pd.DataFrame(df_f['fBodyAccJerk-Y'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-MeanFreq-2'})
            z=pd.DataFrame(df_f['fBodyAccJerk-Z'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-MeanFreq-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # fBodyAccJerk-Skewness-1            
            # fBodyAccJerk-Kurtosis-1            
            # fBodyAccJerk-Skewness-2            
            # fBodyAccJerk-Kurtosis-2            
            # fBodyAccJerk-Skewness-3            
            # fBodyAccJerk-Kurtosis-3
            x=pd.DataFrame(df_f['fBodyAccJerk-X'].apply(lambda x: skew(x))).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-Skewness-1'})
            y=pd.DataFrame(df_f['fBodyAccJerk-Y'].apply(lambda x: skew(x))).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-Skewness-2'})
            z=pd.DataFrame(df_f['fBodyAccJerk-Z'].apply(lambda x: skew(x))).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-Skewness-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            x=pd.DataFrame(df_f['fBodyAccJerk-X'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyAccJerk-X':'fBodyAccJerk-Kurtosis-1'})
            y=pd.DataFrame(df_f['fBodyAccJerk-Y'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyAccJerk-Y':'fBodyAccJerk-Kurtosis-2'})
            z=pd.DataFrame(df_f['fBodyAccJerk-Z'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyAccJerk-Z':'fBodyAccJerk-Kurtosis-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            #fBodyAccJerk-BandsEnergy-X-1
            #fBodyAccJerk-BandsEnergy-X-2
            #fBodyAccJerk-BandsEnergy-X-3
            #fBodyAccJerk-BandsEnergy-X-4
            #fBodyAccJerk-BandsEnergy-X-5
            #fBodyAccJerk-BandsEnergy-X-6 
            #fBodyAccJerk-BandsEnergy-X-7 
            #fBodyAccJerk-BandsEnergy-X-8 
            #fBodyAccJerk-BandsEnergy-X-9 
            #fBodyAccJerk-BandsEnergy-X-10
            #fBodyAccJerk-BandsEnergy-X-11
            #fBodyAccJerk-BandsEnergy-X-12
            #fBodyAccJerk-BandsEnergy-X-13
            #fBodyAccJerk-BandsEnergy-X-14
            #fBodyAccJerk-BandsEnergy-X-15
            #fBodyAccJerk-BandsEnergy-Y-1
            #fBodyAccJerk-BandsEnergy-Y-2
            #fBodyAccJerk-BandsEnergy-Y-3
            #fBodyAccJerk-BandsEnergy-Y-4
            #fBodyAccJerk-BandsEnergy-Y-5
            #fBodyAccJerk-BandsEnergy-Y-6 
            #fBodyAccJerk-BandsEnergy-Y-7 
            #fBodyAccJerk-BandsEnergy-Y-8 
            #fBodyAccJerk-BandsEnergy-Y-9 
            #fBodyAccJerk-BandsEnergy-Y-10
            #fBodyAccJerk-BandsEnergy-Y-11
            #fBodyAccJerk-BandsEnergy-Y-12
            #fBodyAccJerk-BandsEnergy-Y-13
            #fBodyAccJerk-BandsEnergy-Y-14
            #fBodyAccJerk-BandsEnergy-Y-15
            #fBodyAccJerk-BandsEnergy-Z-1
            #fBodyAccJerk-BandsEnergy-Z-2
            #fBodyAccJerk-BandsEnergy-Z-3
            #fBodyAccJerk-BandsEnergy-Z-4
            #fBodyAccJerk-BandsEnergy-Z-5
            #fBodyAccJerk-BandsEnergy-Z-6 
            #fBodyAccJerk-BandsEnergy-Z-7 
            #fBodyAccJerk-BandsEnergy-Z-8 
            #fBodyAccJerk-BandsEnergy-Z-9 
            #fBodyAccJerk-BandsEnergy-Z-10
            #fBodyAccJerk-BandsEnergy-Z-11
            #fBodyAccJerk-BandsEnergy-Z-12
            #fBodyAccJerk-BandsEnergy-Z-13
            #fBodyAccJerk-BandsEnergy-Z-14
            #fBodyAccJerk-BandsEnergy-Z-15
            
            maxbands = 15 # This is num of bands for 50hz, 10 seconds file
            nbands = np.sqrt(len(freqbuckets))
            if (nbands < 5):
                nbands = len(freqbuckets) # Set better minimum number of bands
            fbucketlist = np.array_split(freqbuckets, nbands)
            
            #df_feature_test = df_feature
            
            for var in ['X', 'Y', 'Z']:
                incolname = 'fBodyAccJerk-%s' % var
                startind = 0
                for i in np.arange(maxbands):
                    cname = "fBodyAccJerk-BandsEnergy-%s-%s" % (var, i+1)
                    try:
                        # If i is a valid index of fbucketlist, create column
                        band = fbucketlist[i]
                        bandinds = np.arange(startind, startind+len(band))
                        print("Creating column %s" % cname)
                        df_feature.append(pd.DataFrame(df_f[incolname].apply(lambda x: np.sqrt(sum([y**2 for y in x[bandinds]]))).rename(columns={incolname:cname}).reset_index(drop=True)).rename(columns={0:cname}))
                        startind += len(bandinds)
                    except:
                        # i is not a valid index, fill column with NAN
                        print("No more bands, filling column %s with NANs" % cname)
                        df_feature.append(pd.DataFrame(np.full((2220, 1), fill_value=np.NAN)).rename(columns={0:cname}))
            
            # fBodyGyro-Mean-1                
            # fBodyGyro-Mean-2                
            # fBodyGyro-Mean-3  
            df_feature.append(df_f[['fBodyGyro-X']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyGyro-X':'fBodyGyro-Mean-1'}))
            df_feature.append(df_f[['fBodyGyro-Y']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyGyro-Y':'fBodyGyro-Mean-2'}))
            df_feature.append(df_f[['fBodyGyro-Z']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyGyro-Z':'fBodyGyro-Mean-3'}))
    
            # fBodyGyro-STD-1                 
            # fBodyGyro-STD-2                 
            # fBodyGyro-STD-3
            df_feature.append(df_f[['fBodyGyro-X']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyGyro-X':'fBodyGyro-STD-1'}))
            df_feature.append(df_f[['fBodyGyro-Y']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyGyro-Y':'fBodyGyro-STD-2'}))
            df_feature.append(df_f[['fBodyGyro-Z']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyGyro-Z':'fBodyGyro-STD-3'}))
    
            # fBodyGyro-Mad-1                 
            # fBodyGyro-Mad-2                 
            # fBodyGyro-Mad-3
            df_feature.append(df_f[['fBodyGyro-X']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyGyro-X':'fBodyGyro-Mad-1'}))
            df_feature.append(df_f[['fBodyGyro-Y']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyGyro-Y':'fBodyGyro-Mad-2'}))
            df_feature.append(df_f[['fBodyGyro-Z']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyGyro-Z':'fBodyGyro-Mad-3'}))
    
            # fBodyGyro-Max-1                 
            # fBodyGyro-Max-2                 
            # fBodyGyro-Max-3                 
            df_feature.append(df_f[['fBodyGyro-X']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyGyro-X':'fBodyGyro-Max-1'}))
            df_feature.append(df_f[['fBodyGyro-Y']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyGyro-Y':'fBodyGyro-Max-2'}))
            df_feature.append(df_f[['fBodyGyro-Z']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyGyro-Z':'fBodyGyro-Max-3'}))
    
            # fBodyGyro-Min-1                 
            # fBodyGyro-Min-2                 
            # fBodyGyro-Min-3
            df_feature.append(df_f[['fBodyGyro-X']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyGyro-X':'fBodyGyro-Min-1'}))
            df_feature.append(df_f[['fBodyGyro-Y']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyGyro-Y':'fBodyGyro-Min-2'}))
            df_feature.append(df_f[['fBodyGyro-Z']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyGyro-Z':'fBodyGyro-Min-3'}))
                 
            # fBodyGyro-SMA-1
            t = df_f[['fBodyGyro-X','fBodyGyro-Y','fBodyGyro-Z']].abs().sum(axis=1)
            t = pd.DataFrame(t.apply(lambda row: sum(row))).rename(columns={0:'fBodyGyro-SMA-1'})
            df_feature.append(t)
            
            # fBodyGyro-Energy-1              
            # fBodyGyro-Energy-2              
            # fBodyGyro-Energy-3 
            t = np.square(df_f[['fBodyGyro-X']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyGyro-X':'fBodyGyro-Energy-1'})
            df_feature.append(t)
            t = np.square(df_f[['fBodyGyro-Y']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyGyro-Y':'fBodyGyro-Energy-2'})
            df_feature.append(t)
            t = np.square(df_f[['fBodyGyro-Z']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyGyro-Z':'fBodyGyro-Energy-3'})
            df_feature.append(t)
            
            # fBodyGyro-IQR-1                 
            # fBodyGyro-IQR-2                 
            # fBodyGyro-IQR-3
            x=df_f['fBodyGyro-X'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyGyro-IQR-1'})
            y=df_f['fBodyGyro-Y'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyGyro-IQR-2'})
            z=df_f['fBodyGyro-Z'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyGyro-IQR-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # fBodyGyro-ropy-1                
            # fBodyGyro-ropy-1                
            # fBodyGyro-ropy-1   
            x=pd.DataFrame(df_f['fBodyGyro-X'].apply(lambda row: entropy(row))).rename(columns={0:'fBodyGyro-ropy-1'})
            y=pd.DataFrame(df_f['fBodyGyro-Y'].apply(lambda row: entropy(row))).rename(columns={0:'fBodyGyro-ropy-2'})
            z=pd.DataFrame(df_f['fBodyGyro-Z'].apply(lambda row: entropy(row))).rename(columns={0:'fBodyGyro-ropy-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # fBodyGyro-MaxInds-1             
            # fBodyGyro-MaxInds-2             
            # fBodyGyro-MaxInds-3
            x=pd.DataFrame(df_f['fBodyGyro-X'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyGyro-X':'fBodyGyro-MaxInds-1'})
            y=pd.DataFrame(df_f['fBodyGyro-Y'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyGyro-Y':'fBodyGyro-MaxInds-2'})
            z=pd.DataFrame(df_f['fBodyGyro-Z'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyGyro-Z':'fBodyGyro-MaxInds-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # Get frequency buckets for this sampling profile
            freqbuckets = np.fft.rfftfreq(hz*seconds, 1/hz)
            
            # fBodyGyro-MeanFreq-1            
            # fBodyGyro-MeanFreq-2            
            # fBodyGyro-MeanFreq-3 
            x=pd.DataFrame(df_f['fBodyGyro-X'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyGyro-X':'fBodyGyro-MeanFreq-1'})
            y=pd.DataFrame(df_f['fBodyGyro-Y'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyGyro-Y':'fBodyGyro-MeanFreq-2'})
            z=pd.DataFrame(df_f['fBodyGyro-Z'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyGyro-Z':'fBodyGyro-MeanFreq-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            # fBodyGyro-Skewness-1            
            # fBodyGyro-Kurtosis-1            
            # fBodyGyro-Skewness-2            
            # fBodyGyro-Kurtosis-2            
            # fBodyGyro-Skewness-3            
            # fBodyGyro-Kurtosis-3
            x=pd.DataFrame(df_f['fBodyGyro-X'].apply(lambda x: skew(x))).rename(columns={'fBodyGyro-X':'fBodyGyro-Skewness-1'})
            y=pd.DataFrame(df_f['fBodyGyro-Y'].apply(lambda x: skew(x))).rename(columns={'fBodyGyro-Y':'fBodyGyro-Skewness-2'})
            z=pd.DataFrame(df_f['fBodyGyro-Z'].apply(lambda x: skew(x))).rename(columns={'fBodyGyro-Z':'fBodyGyro-Skewness-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)
            
            x=pd.DataFrame(df_f['fBodyGyro-X'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyGyro-X':'fBodyGyro-Kurtosis-1'})
            y=pd.DataFrame(df_f['fBodyGyro-Y'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyGyro-Y':'fBodyGyro-Kurtosis-2'})
            z=pd.DataFrame(df_f['fBodyGyro-Z'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyGyro-Z':'fBodyGyro-Kurtosis-3'})
            df_feature.append(x)  
            df_feature.append(y)
            df_feature.append(z)

            # Energy of frequency bands
            
            #fBodyGyro-BandsEnergy-X-1
            #fBodyGyro-BandsEnergy-X-2
            #fBodyGyro-BandsEnergy-X-3
            #fBodyGyro-BandsEnergy-X-4
            #fBodyGyro-BandsEnergy-X-5
            #fBodyGyro-BandsEnergy-X-6 
            #fBodyGyro-BandsEnergy-X-7 
            #fBodyGyro-BandsEnergy-X-8 
            #fBodyGyro-BandsEnergy-X-9 
            #fBodyGyro-BandsEnergy-X-10
            #fBodyGyro-BandsEnergy-X-11
            #fBodyGyro-BandsEnergy-X-12
            #fBodyGyro-BandsEnergy-X-13
            #fBodyGyro-BandsEnergy-X-14
            #fBodyGyro-BandsEnergy-X-15
            #fBodyGyro-BandsEnergy-Y-1
            #fBodyGyro-BandsEnergy-Y-2
            #fBodyGyro-BandsEnergy-Y-3
            #fBodyGyro-BandsEnergy-Y-4
            #fBodyGyro-BandsEnergy-Y-5
            #fBodyGyro-BandsEnergy-Y-6 
            #fBodyGyro-BandsEnergy-Y-7 
            #fBodyGyro-BandsEnergy-Y-8 
            #fBodyGyro-BandsEnergy-Y-9 
            #fBodyGyro-BandsEnergy-Y-10
            #fBodyGyro-BandsEnergy-Y-11
            #fBodyGyro-BandsEnergy-Y-12
            #fBodyGyro-BandsEnergy-Y-13
            #fBodyGyro-BandsEnergy-Y-14
            #fBodyGyro-BandsEnergy-Y-15
            #fBodyGyro-BandsEnergy-Z-1
            #fBodyGyro-BandsEnergy-Z-2
            #fBodyGyro-BandsEnergy-Z-3
            #fBodyGyro-BandsEnergy-Z-4
            #fBodyGyro-BandsEnergy-Z-5
            #fBodyGyro-BandsEnergy-Z-6 
            #fBodyGyro-BandsEnergy-Z-7 
            #fBodyGyro-BandsEnergy-Z-8 
            #fBodyGyro-BandsEnergy-Z-9 
            #fBodyGyro-BandsEnergy-Z-10
            #fBodyGyro-BandsEnergy-Z-11
            #fBodyGyro-BandsEnergy-Z-12
            #fBodyGyro-BandsEnergy-Z-13
            #fBodyGyro-BandsEnergy-Z-14
            #fBodyGyro-BandsEnergy-Z-15
            
            '''
            Note that since num of frequency buckets = hz*seconds/2 + 1,
            each file may have a different number of bands available. Here
            we split the frequency bucket list into sqrt(len(freqbuckets)))
            separate chunks because it seems like a reasonable number, then 
            calculate the energy of each set of bands, then pad the number 
            of resulting columns with all-NA columns so that each data set
            has an equivalent number of columns (for easier future processing).
            '''
            
            maxbands = 15 # This is num of bands for 50hz, 10 seconds file
            nbands = np.sqrt(len(freqbuckets))
            if (nbands < 5):
                nbands = len(freqbuckets) # Set better minimum number of bands
            fbucketlist = np.array_split(freqbuckets, nbands)
            
            #df_feature_test = df_feature
            
            for var in ['X', 'Y', 'Z']:
                incolname = 'fBodyGyro-%s' % var
                startind = 0
                for i in np.arange(maxbands):
                    cname = "fBodyGyro-BandsEnergy-%s-%s" % (var, i+1)
                    try:
                        # If i is a valid index of fbucketlist, create column
                        band = fbucketlist[i]
                        bandinds = np.arange(startind, startind+len(band))
                        print("Creating column %s" % cname)
                        df_feature.append(pd.DataFrame(df_f[incolname].apply(lambda x: np.sqrt(sum([y**2 for y in x[bandinds]]))).rename(columns={incolname:cname}).reset_index(drop=True)).rename(columns={0:cname}))
                        startind += len(bandinds)
                    except:
                        # i is not a valid index, fill column with NAN
                        print("No more bands, filling column %s with NANs" % cname)
                        df_feature.append(pd.DataFrame(np.full((2220, 1), fill_value=np.NAN)).rename(columns={0:cname}))
            
            # fBodyAccMag-Mean-1                
            df_feature.append(df_f[['fBodyAccMag']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyAccMag':'fBodyAccMag-Mean-1'}))
    
            # fBodyAccMag-STD-1                 
            df_feature.append(df_f[['fBodyAccMag']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyAccMag':'fBodyAccMag-STD-1'}))
    
            # fBodyAccMag-Mad-1                 
            df_feature.append(df_f[['fBodyAccMag']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyAccMag':'fBodyAccMag-Mad-1'}))
    
            # fBodyAccMag-Max-1                               
            df_feature.append(df_f[['fBodyAccMag']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyAccMag':'fBodyAccMag-Max-1'}))
    
            # fBodyAccMag-Min-1                 
            df_feature.append(df_f[['fBodyAccMag']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyAccMag':'fBodyAccMag-Min-1'}))
                 
            # fBodyAccMag-SMA-1
            t = df_f[['fBodyAccMag']].abs().sum(axis=1)
            t = pd.DataFrame(t.apply(lambda row: sum(row))).rename(columns={0:'fBodyAccMag-SMA-1'})
            df_feature.append(t)
            
            # fBodyAccMag-Energy-1              
            t = np.square(df_f[['fBodyAccMag']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyAccMag':'fBodyAccMag-Energy-1'})
            df_feature.append(t)
            
            # fBodyAccMag-IQR-1                 
            x=df_f['fBodyAccMag'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyAccMag-IQR-1'})
            df_feature.append(x)  
            
            # fBodyAccMag-ropy-1                 
            x=pd.DataFrame(df_f['fBodyAccMag'].apply(lambda row: entropy(row))).rename(columns={'fBodyAccMag':'fBodyAccMag-ropy-1'})
            df_feature.append(x)  

            # fBodyAccMag-MaxInds-1             
            x=pd.DataFrame(df_f['fBodyAccMag'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyAccMag':'fBodyAccMag-MaxInds-1'})
            df_feature.append(x)  

            # Get frequency buckets for this sampling profile
            freqbuckets = np.fft.rfftfreq(hz*seconds, 1/hz)
            
            # fBodyAccMag-MeanFreq-1            
            # fBodyAccMag-MeanFreq-2            
            # fBodyAccMag-MeanFreq-3 
            x=pd.DataFrame(df_f['fBodyAccMag'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyAccMag':'fBodyAccMag-MeanFreq-1'})
            df_feature.append(x)
            
            # fBodyAccMag-Skewness-1            
            # fBodyAccMag-Kurtosis-1            
            x=pd.DataFrame(df_f['fBodyAccMag'].apply(lambda x: skew(x))).rename(columns={'fBodyAccMag':'fBodyAccMag-Skewness-1'})
            df_feature.append(x)  
            
            x=pd.DataFrame(df_f['fBodyAccMag'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyAccMag':'fBodyAccMag-Kurtosis-1'})
            df_feature.append(x)  
                     
            # fBodyAccJerkMag-Mean-1                
            df_feature.append(df_f[['fBodyAccJerkMag']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-Mean-1'}))
    
            # fBodyAccJerkMag-STD-1                 
            df_feature.append(df_f[['fBodyAccJerkMag']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-STD-1'}))
    
            # fBodyAccJerkMag-Mad-1                 
            df_feature.append(df_f[['fBodyAccJerkMag']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-Mad-1'}))
    
            # fBodyAccJerkMag-Max-1                               
            df_feature.append(df_f[['fBodyAccJerkMag']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-Max-1'}))
    
            # fBodyAccJerkMag-Min-1                 
            df_feature.append(df_f[['fBodyAccJerkMag']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-Min-1'}))
                 
            # fBodyAccJerkMag-SMA-1
            t = df_f[['fBodyAccJerkMag']].abs().sum(axis=1)
            t = pd.DataFrame(t.apply(lambda row: sum(row))).rename(columns={0:'fBodyAccJerkMag-SMA-1'})
            df_feature.append(t)
            
            # fBodyAccJerkMag-Energy-1              
            t = np.square(df_f[['fBodyAccJerkMag']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-Energy-1'})
            df_feature.append(t)
            
            # fBodyAccJerkMag-IQR-1                 
            x=df_f['fBodyAccJerkMag'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyAccJerkMag-IQR-1'})
            df_feature.append(x)  
            
            # fBodyAccJerkMag-ropy-1                 
            x=pd.DataFrame(df_f['fBodyAccJerkMag'].apply(lambda row: entropy(row))).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-ropy-1'})
            df_feature.append(x)  

            # fBodyAccJerkMag-MaxInds-1             
            x=pd.DataFrame(df_f['fBodyAccJerkMag'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-MaxInds-1'})
            df_feature.append(x)  

            # Get frequency buckets for this sampling profile
            freqbuckets = np.fft.rfftfreq(hz*seconds, 1/hz)
            
            # fBodyAccJerkMag-MeanFreq-1            
            # fBodyAccJerkMag-MeanFreq-2            
            # fBodyAccJerkMag-MeanFreq-3 
            x=pd.DataFrame(df_f['fBodyAccJerkMag'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-MeanFreq-1'})
            df_feature.append(x)
            
            # fBodyAccJerkMag-Skewness-1            
            # fBodyAccJerkMag-Kurtosis-1            
            x=pd.DataFrame(df_f['fBodyAccJerkMag'].apply(lambda x: skew(x))).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-Skewness-1'})
            df_feature.append(x)  
            
            x=pd.DataFrame(df_f['fBodyAccJerkMag'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyAccJerkMag':'fBodyAccJerkMag-Kurtosis-1'})
            df_feature.append(x)  
            
            # fBodyGyroMag-Mean-1                
            df_feature.append(df_f[['fBodyGyroMag']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyGyroMag':'fBodyGyroMag-Mean-1'}))
    
            # fBodyGyroMag-STD-1                 
            df_feature.append(df_f[['fBodyGyroMag']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyGyroMag':'fBodyGyroMag-STD-1'}))
    
            # fBodyGyroMag-Mad-1                 
            df_feature.append(df_f[['fBodyGyroMag']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyGyroMag':'fBodyGyroMag-Mad-1'}))
    
            # fBodyGyroMag-Max-1                               
            df_feature.append(df_f[['fBodyGyroMag']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyGyroMag':'fBodyGyroMag-Max-1'}))
    
            # fBodyGyroMag-Min-1                 
            df_feature.append(df_f[['fBodyGyroMag']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyGyroMag':'fBodyGyroMag-Min-1'}))
                 
            # fBodyGyroMag-SMA-1
            t = df_f[['fBodyGyroMag']].abs().sum(axis=1)
            t = pd.DataFrame(t.apply(lambda row: sum(row))).rename(columns={0:'fBodyGyroMag-SMA-1'})
            df_feature.append(t)
            
            # fBodyGyroMag-Energy-1              
            t = np.square(df_f[['fBodyGyroMag']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyGyroMag':'fBodyGyroMag-Energy-1'})
            df_feature.append(t)
            
            # fBodyGyroMag-IQR-1                 
            x=df_f['fBodyGyroMag'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyGyroMag-IQR-1'})
            df_feature.append(x)  
            
            # fBodyGyroMag-ropy-1                 
            x=pd.DataFrame(df_f['fBodyGyroMag'].apply(lambda row: entropy(row))).rename(columns={'fBodyGyroMag':'fBodyGyroMag-ropy-1'})
            df_feature.append(x)  

            # fBodyGyroMag-MaxInds-1             
            x=pd.DataFrame(df_f['fBodyGyroMag'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyGyroMag':'fBodyGyroMag-MaxInds-1'})
            df_feature.append(x)  

            # Get frequency buckets for this sampling profile
            freqbuckets = np.fft.rfftfreq(hz*seconds, 1/hz)
            
            # fBodyGyroMag-MeanFreq-1            
            # fBodyGyroMag-MeanFreq-2            
            # fBodyGyroMag-MeanFreq-3 
            x=pd.DataFrame(df_f['fBodyGyroMag'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyGyroMag':'fBodyGyroMag-MeanFreq-1'})
            df_feature.append(x)
            
            # fBodyGyroMag-Skewness-1            
            # fBodyGyroMag-Kurtosis-1            
            x=pd.DataFrame(df_f['fBodyGyroMag'].apply(lambda x: skew(x))).rename(columns={'fBodyGyroMag':'fBodyGyroMag-Skewness-1'})
            df_feature.append(x)  
            
            x=pd.DataFrame(df_f['fBodyGyroMag'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyGyroMag':'fBodyGyroMag-Kurtosis-1'})
            df_feature.append(x)   
            
            # fBodyGyroJerkMag-Mean-1                
            df_feature.append(df_f[['fBodyGyroJerkMag']].apply(lambda row: [np.mean(y) for y in row]).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-Mean-1'}))
    
            # fBodyGyroJerkMag-STD-1                 
            df_feature.append(df_f[['fBodyGyroJerkMag']].apply(lambda row: [np.std(y) for y in row]).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-STD-1'}))
    
            # fBodyGyroJerkMag-Mad-1                 
            df_feature.append(df_f[['fBodyGyroJerkMag']].apply(lambda row: [mad2(y) for y in row]).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-Mad-1'}))
    
            # fBodyGyroJerkMag-Max-1                               
            df_feature.append(df_f[['fBodyGyroJerkMag']].apply(lambda row: [np.max(y) for y in row]).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-Max-1'}))
    
            # fBodyGyroJerkMag-Min-1                 
            df_feature.append(df_f[['fBodyGyroJerkMag']].apply(lambda row: [np.min(y) for y in row]).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-Min-1'}))
                 
            # fBodyGyroJerkMag-SMA-1
            t = df_f[['fBodyGyroJerkMag']].abs().sum(axis=1)
            t = pd.DataFrame(t.apply(lambda row: sum(row))).rename(columns={0:'fBodyGyroJerkMag-SMA-1'})
            df_feature.append(t)
            
            # fBodyGyroJerkMag-Energy-1              
            t = np.square(df_f[['fBodyGyroJerkMag']])
            a = t.apply(lambda row: [sum(y) for y in row])
            b = t.apply(lambda x: [len(y) for y in x])
            t=(a/b).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-Energy-1'})
            df_feature.append(t)
            
            # fBodyGyroJerkMag-IQR-1                 
            x=df_f['fBodyGyroJerkMag'].apply(lambda row: pd.DataFrame(row).quantile(0.75)-pd.DataFrame(row).quantile(0.25)).rename(columns={0:'fBodyGyroJerkMag-IQR-1'})
            df_feature.append(x)  
            
            # fBodyGyroJerkMag-ropy-1                 
            x=pd.DataFrame(df_f['fBodyGyroJerkMag'].apply(lambda row: entropy(row))).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-ropy-1'})
            df_feature.append(x)  

            # fBodyGyroJerkMag-MaxInds-1             
            x=pd.DataFrame(df_f['fBodyGyroJerkMag'].apply(lambda x: np.argmax(x))).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-MaxInds-1'})
            df_feature.append(x)  

            # Get frequency buckets for this sampling profile
            freqbuckets = np.fft.rfftfreq(hz*seconds, 1/hz)
            
            # fBodyGyroJerkMag-MeanFreq-1            
            # fBodyGyroJerkMag-MeanFreq-2            
            # fBodyGyroJerkMag-MeanFreq-3 
            x=pd.DataFrame(df_f['fBodyGyroJerkMag'].apply(lambda x: sum([x[i]*freqbuckets[i] for i in np.arange(len(x))])/len(x))).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-MeanFreq-1'})
            df_feature.append(x)
            
            # fBodyGyroJerkMag-Skewness-1            
            # fBodyGyroJerkMag-Kurtosis-1            
            x=pd.DataFrame(df_f['fBodyGyroJerkMag'].apply(lambda x: skew(x))).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-Skewness-1'})
            df_feature.append(x)  
            
            x=pd.DataFrame(df_f['fBodyGyroJerkMag'].apply(lambda x: kurtosis(x))).rename(columns={'fBodyGyroJerkMag':'fBodyGyroJerkMag-Kurtosis-1'})
            df_feature.append(x)   
            
            # tBodyAcc-AngleWRTGravity-1     
            # tBodyAccJerk-AngleWRTGravity-1 
            # tBodyGyro-AngleWRTGravity-1    
            # tBodyGyroJerk-AngleWRTGravity-1
            # tXAxisAcc-AngleWRTGravity-1    
            # tYAxisAcc-AngleWRTGravity-1    
            # tZAxisAcc-AngleWRTGravity-1    
        
            largedf=pd.concat(df_feature, axis=1)
            print(str(ct)+'/4 Printing: '+str(hz)+'hz'+str(seconds)+'s.csv')
            largedf.to_csv(str(hz)+'hz'+str(seconds)+'s.csv',sep='\t')
    
    
if __name__ == '__main__':
    feature_extract()