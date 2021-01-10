# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 09:03:15 2020

@author: Matt Bayer
"""



import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

import covid

#%% Load data

state = covid.read_covid_data_wi('state')
county = covid.read_covid_data_wi('county')
mke = county[county.NAME == 'Milwaukee']

# rename
col_rename = {'Date': 'Date', 'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
state = state.rename(columns=col_rename)
mke = mke.rename(columns=col_rename)



#%% Compare with deaths by death date

def read_death_raw(death_file):
    death_raw = pd.read_csv(death_file)
    # Note: key is to download the file and then re-save it in Excel specifically
    # as csv, otherwise it's actually tab delimited and harder to read in in python
    
    death = death_raw.iloc[:,2:]
    death = death.rename(columns={'Unnamed: 2': 'series'})
    death.iloc[0,0] = 'datestring'
    death = death.set_index('series').T.reset_index(drop=True)
    death.columns.name = ''
    
    # hack because the date string does not include the year
    death.loc[0:344, 'datestring'] = death.loc[0:344, 'datestring'] + '-2020'
    death.loc[345:, 'datestring'] = death.loc[345:, 'datestring'] + '-2021'
    
    death['Date'] = pd.to_datetime(death['datestring'])
        
    death = death.set_index('Date')
    
    return death

death_03 = read_death_raw('.\\data\\Deaths by day stacked_2020-12-03.csv')
death_04 = read_death_raw('.\\data\\Deaths by day stacked_2020-12-04.csv')
death_10 = read_death_raw('.\\data\\Deaths by day stacked_2020-12-10.csv')
death_21 = read_death_raw('.\\data\\Deaths by day stacked_2020-12-21.csv')
death_29 = read_death_raw('.\\data\\Deaths by day stacked_2020-12-29.csv')
death_latest = read_death_raw('.\\data\\Deaths by day stacked_2021-01-08.csv')

latest = 'Deaths 08-Jan'

death = death_latest
death['Deaths 3-Dec'] = pd.to_numeric(death_03['Confirm + Probable deaths'])
death['Deaths 4-Dec'] = pd.to_numeric(death_04['Confirm + Probable deaths'])
death['Deaths 10-Dec'] = pd.to_numeric(death_10['Confirm + Probable deaths'])
death['Deaths 21-Dec'] = pd.to_numeric(death_21['Confirmed deaths'])
death['Deaths 29-Dec'] = pd.to_numeric(death_29['Confirmed deaths'])
death[latest] = pd.to_numeric(death_latest['Confirmed deaths'])
death['Deaths (reported)'] = state.set_index('Date')['Deaths']

# compare = 'Deaths 4-Dec'
compare = 'Deaths 29-Dec'

death.rolling(7).mean().plot(y=[latest, 'Deaths (reported)'], title='Date of Death vs. Report (7-day avg)')
death['Difference'] = death[latest] - death[compare]
death.plot(y=[compare, latest, 'Difference'], title='Date of Death, '+compare+' vs. '+latest)


# seems like a huge delay in deaths... but if there is such a big delay, then
# I can't trust the deaths-by-date curve right now either, and you would have
# to expect continued large numbers of reports coming in for past days.

#%% Plot delay in cases

# Cases by test date for Wisconsin
filename = '.\data\Cases_with_prob_stacked_data_2021-01-08.csv'
case_latest = 'Cases 20-Dec'
death_latest = latest;

cases = pd.read_csv(filename)
# filter out redundant data
cases = cases.loc[cases['Measure Names'] == 'Confirmed cases']  
# rename columns
col_rename = {'Day of Epi Dt': 'Date', 'Stacked Confirm + Probable cases': case_latest}
cases = cases[col_rename.keys()]
cases = cases.rename(columns=col_rename)
cases['Date'] = pd.to_datetime(cases['Date'])

# add reported cases and deaths; set index as date temporarily so they merge correctly
cases = cases.set_index('Date')
cases['Cases (reported)'] = state.set_index('Date').Cases

death2 = death.reset_index(drop=False)
death2['Date'] = death2['Date'] - datetime.timedelta(days=18)
cases[death_latest] = death2.set_index('Date')[death_latest] / 0.012
cases = cases.reset_index(drop=False)

cases.plot(x='Date', y=[case_latest, 'Cases (reported)'])

cases.plot(x='Date', y=[case_latest, death_latest])



