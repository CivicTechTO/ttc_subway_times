# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 20:36:38 2019

@author: erwin
"""

import numpy as np;  # useful for many scientific computing in Python
import pandas as pd; # primary data structure library
import datetime; # datetime data

# data from 201907.zip were used
#responses = pd.read_csv('responses_2019-03.csv'); # import file
#requests = pd.read_csv('requests_2019-03.csv'); # import file

responses = pd.read_csv('responses.csv'); # import file
requests = pd.read_csv('requests.csv'); # import file

# merge two dataframes
df = pd.merge(left=responses, right=requests, left_on='requestid',
                  right_on='requestid');
              
              
## Line 2 (BD) trains
trains_BD = df[df['subwayline'] == 'BD'].copy();

# separate date and time
r_date = pd.to_datetime(trains_BD['request_date']);

trains_BD['date'] = r_date.dt.date;
trains_BD['time'] = r_date.dt.time;

# On weekdays and Saturdays, trains run from about 6 a.m. until 1:30 a.m. 
# On Sundays, they run from about 8 a.m. to 1:30 a.m.
# Take data from 6am to 1:30am everyday

trains_BD = trains_BD[(trains_BD['time']>=datetime.time( 6,0,0 )) |
                      (trains_BD['time']<=datetime.time( 1,30,0 )) ];
        
        
        
# Find trains at station
trains_BD_AtStation = trains_BD[trains_BD['train_message'] == 'AtStation'];

# Find trains arriving between 0 to 2 min exclusive
trains_BD_Delayed = trains_BD[(trains_BD['train_message'] == 'Delayed') &
                              (trains_BD['timint'] <2) &
                              (trains_BD['timint'] >0)];

trains_BD_Arriving = trains_BD[(trains_BD['train_message'] == 'Arriving') &
                              (trains_BD['timint'] <2) &
                              (trains_BD['timint'] >0)]; 

                               
## Concatenate three dataframes
merged = pd.concat([trains_BD_AtStation, trains_BD_Arriving], axis=0);
merged = pd.concat([merged, trains_BD_Delayed], axis=0);

# If trains are arriving or delayed in two stations, 
# keep the one takes shorter time to arrive or the first one

# sort based on Time remaining until train arrives at station (timint)
merged = pd.concat((trains_BD_AtStation.sort_values(
        by=['timint']), trains_BD_Arriving.sort_values(by=['timint'])), axis=0);
        
merged = pd.concat((merged, trains_BD_Delayed.sort_values(
        by=['timint'])), axis=0);
l1 = len(merged); # store length for comparison

## Now it should be in the order AtStation / timint(ascending) -> Arriving / timint(ascending) -> Delayed / timint(ascending)
# remove duplicates
merged.drop_duplicates(subset=['trainid','create_date'],keep='first',inplace=True);

print('Number of duplicates = ', l1-len(merged));

merged[merged.duplicated(subset=['trainid','create_date'], keep=False)]

# Switch stationid
merged.loc[df['stationid'] == 9, 'stationid'] = 47;
merged.loc[df['stationid'] == 10, 'stationid'] = 48;
merged.loc[df['stationid'] == 22, 'stationid'] = 50;

# remove directionality in station_char
merged['station_char'] = merged['station_char'].str[:-1];

# sort
merged.sort_values(by=['date','trainid','time'], inplace=True);

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


# merged.to_csv('merged_2019_04.csv')
