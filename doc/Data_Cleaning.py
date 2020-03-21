# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 20:36:38 2019

@author: erwin
"""

####################################################################
# This file runs algorithms included in arrival_time_exploration_All_Lines.ipynb
# It dose not drop rows with Sort_error
# But it outputs a txt file including the index of rows with Sort_error
# so that they can be easily excluded

######################################
# Save print statements to txt file
import sys;
file = open('output_0.txt', 'a');
sys.stdout = file;
######################################

import numpy as np;  # useful for many scientific computing in Python
import pandas as pd; # primary data structure library
import datetime; # datetime data

responses = pd.read_csv('responses_09.csv'); # import file
requests = pd.read_csv('requests_09.csv'); # import file

# merge two dataframes
df = pd.merge(left=responses, right=requests, left_on='requestid',
                  right_on='requestid');
              
# separate date and time
r_date = pd.to_datetime(df['create_date']);

df['date'] = r_date.dt.date;
df['time'] = r_date.dt.time;

# On weekdays and Saturdays, trains run from about 6 a.m. until 1:30 a.m. 
# On Sundays, they run from about 8 a.m. to 1:30 a.m.
# Take data from 6am to 1:30am everyday

df = df[(df['time']>=datetime.time( 6,0,0 )) |
                      (df['time']<=datetime.time( 1,30,0 )) ];
        
        
        
# Find trains at station
df_AtStation = df[df['train_message'] == 'AtStation'];

# Find trains arriving between 0 to 2 min exclusive
#df_Delayed = df[(df['train_message'] == 'Delayed') &
#                              (df['timint'] <2) &
#                              (df['timint'] >0)];
#
#df_Arriving = df[(df['train_message'] == 'Arriving') &
#                              (df['timint'] <2) &
#                              (df['timint'] >0)]; 

# drop delayed and timint == 0
df_Delayed = df[(df['train_message'] == 'Delayed') &
                              (df['timint'] == 0)];

df_Arriving = df[(df['train_message'] == 'Arriving')];

####################################################################
# drop duplicates
                 
# If trains are arriving or delayed in two stations, 
# keep the one takes shorter time to arrive or the first one

# sort based on Time remaining until train arrives at station (timint)
merged = pd.concat((df_AtStation.sort_values(
        by=['timint']), df_Arriving.sort_values(by=['timint'])), axis=0);
        
merged = pd.concat((merged, df_Delayed.sort_values(
        by=['timint'])), axis=0);
l1 = len(merged); # store length for comparison

## Now it should be in the order AtStation / timint(ascending) -> Arriving / timint(ascending) -> Delayed / timint(ascending)
# remove duplicates
# use request_date because there are three rows per request_date
merged.drop_duplicates(subset=['trainid','request_date'],keep='first',inplace=True);

print('Number of duplicates = ', l1-len(merged));

# merged[merged.duplicated(subset=['trainid','create_date'], keep=False)];

################################################################
# Drop unnecessary columns

# check system_message_type to be Normal
a = sorted(merged['system_message_type']);
if a[0] == a[-1]:
    merged.drop(['system_message_type'],axis=1, inplace=True);
else:
    print('system_message_type coloumn is not all Normal');

# check data_ to be nan
if np.isnan(np.min(merged['data_'])):
    merged.drop(['data_'],axis=1, inplace=True);
else:
    print('data_ coloumn is not all nan');
    
# check all_stations to be success
a = sorted(merged['all_stations']);
if a[0] == a[-1]:
    merged.drop(['all_stations'],axis=1, inplace=True);
else:
    print('all_stations coloumn is not all success');
    
# remove directionality in station_char
merged['station_char'] = merged['station_char'].str[:-1];

#######################################################################
# Correct mislabeled rows

# sort by trainid, create_date
merged.sort_values(by=['trainid', 'create_date'], inplace=True);
# reset index
merged.reset_index(drop=True,inplace=True);
# find incorrect assignments of subwayline and lineid
AE = ((merged['subwayline'] == 'YUS' ) != (merged['lineid'] == 1)) | ( 
    (merged['subwayline'] == 'BD' ) != (merged['lineid'] == 2)) | (
    (merged['subwayline'] == 'SHEP' ) != (merged['lineid'] == 4));

# create a dataframe of trainid and date
train_error = merged[['trainid','date']].loc[AE==True];
# initiate some variables for debugging purposes
line1_trains = 0;
line2_trains = 0;
line4_trains = 0;
Sort_error = pd.Index([],dtype='int64');

# run loop for each unique trainid, then unique date with this trainid
# then test nearby stations for each line separately
# then correct subwayline & lineid, switch station id 

for i in train_error['trainid'].unique():
    for j in train_error[train_error['trainid']==i]['date'].unique():
            # check if the train stops at Dupont (DUP), Museum(MUS), 
            # York Mills(YKM), North York Centre(NYC), Rosedale (ROS) Wellesley (WEL)
            # if yes, then it is on line 1
        if merged[(merged['trainid']==i) & (merged['date']==j)]['station_char'].str.contains(
            'DUP|MUS|YKM|NYK|ROS|WEL').any():

                # check if the train also stops on line 2 and 4
            if merged[(merged['trainid']==i) & (merged['date']==j)]['station_char'].str.contains(
                'BSS|BAU|BAT|SHE').any():
                print('error in if line 1 section')
                print('error in train', i)
                Sort_error = Sort_error.append( merged[(merged['trainid']==i) & (merged['date']==j)].index);
            # make correction
            merged.loc[(merged['trainid']==i) & (merged['date']==j), 'subwayline'] = 'YUS';
            merged.loc[(merged['trainid']==i) & (merged['date']==j), 'lineid'] = 1;
            
            # add counter
            line1_trains = line1_trains +1;
            
        # check if the train stops at Bay station (BAU), Bathurst (BAT), Sherbourne (SHE)
        # if yes, then it is on line 2
        elif merged[(merged['trainid']==i) & (merged['date']==j)]['station_char'].str.contains('BAU|BAT|SHE').any():
                # check if the train also stops on line 4 because we already checked for line 1 
            if merged[(merged['trainid']==i) & (merged['date']==j)]['station_char'].str.contains(
                'BSS').any():
                print('error in elif line 2 section')
                print('error in train', i)
                Sort_error = Sort_error.append( merged[(merged['trainid']==i) & (merged['date']==j)].index);
            
            # make correction
            merged.loc[(merged['trainid']==i) & (merged['date']==j), 'subwayline'] = 'BD';
            merged.loc[(merged['trainid']==i) & (merged['date']==j), 'lineid'] = 2;
            
            # add counter
            line2_trains = line2_trains +1;

            # check if the train stops at Bessarion (BSS)
            # if yes, then it is on line 4
            # NO NEED to make additional checks
        elif merged[(merged['trainid']==i) & (merged['date']==j)]['station_char'].str.contains('BSS').any():
            
            # make correction
            merged.loc[(merged['trainid']==i) & (merged['date']==j), 'subwayline'] = 'SHEP';
            merged.loc[(merged['trainid']==i) & (merged['date']==j), 'lineid'] = 4;
                        
             # add counter
            line4_trains = line4_trains +1;

        # if no, sorting error
        else:
            print('error in else section')
            print('error in train', i)
            Sort_error = Sort_error.append( merged[(merged['trainid']==i) & (merged['date']==j)].index);

print('# of relabeled line 1 trains: ', line1_trains)
print('# of relabeled line 2 trains: ', line2_trains)
print('# of relabeled line 4 trains: ', line4_trains)            

      
########################################################################
# Correct mislabeled 'stationid'

# find and correct mislabeled stationid
# line 1
merged.loc[(merged['lineid']==1) & (merged['stationid'] == 47), 'stationid'] = 9;
merged.loc[(merged['lineid']==1) & (merged['date']==j) & (merged['stationid'] == 48), 'stationid'] = 10;
merged.loc[(merged['lineid']==1) & (merged['date']==j) & (merged['stationid'] == 50), 'stationid'] = 22;

# line 2
merged.loc[(merged['lineid']==2) & (merged['stationid'] == 9), 'stationid'] = 47;
merged.loc[(merged['lineid']==2) & (merged['stationid'] == 10), 'stationid'] = 48;
merged.loc[(merged['lineid']==2) & (merged['stationid'] == 22), 'stationid'] = 50;

# line 4
merged.loc[(merged['lineid']==4) & (merged['stationid'] == 30), 'stationid'] = 64;

###########################################################
# output data files    
file.close();  

# output dataframe as csv file
merged.to_csv('merged_2019_09.csv');

# output index as numpy npy file
np.save('Sort_error_2019_09.npy', Sort_error.values);
# Use the following code to open npy and convert into Int64Index object:
# x = np.load('Sort_error_2019_04.npy')
# x2 = pd.Index(x)


