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



#%% Read in all death-by-date data

# get all death by date files
file_dates = list()
file_names = list()
deaths = pd.DataFrame({'Date': pd.date_range(start='2020-03-01', end=datetime.date.today())})
deaths = deaths.set_index('Date')

path = 'data'
for file in os.listdir(path):
    if file.startswith('Deaths by day stacked_'):
        name = os.path.join(path, file)
        date = pd.to_datetime(file[-14:-4])

        file_names.append(name)
        file_dates.append(date)

        # read Confirmed deaths, add as column to DataFrame
        temp_deaths = covid.read_deathdate_wi(name).set_index('Date')
        col_name = date.strftime('%#d-%b')        
        deaths[col_name] = temp_deaths['Confirmed deaths']

col_names = deaths.columns
latest = col_names[-1]
compare = col_names[-2]

#%% Plots death by date comparisons

# latest deaths by date and the difference between them
deaths['Latest difference'] = deaths[latest] - deaths[compare]
deaths.plot(y=[latest, compare, 'Latest difference'],
            title='Date of Death, '+latest+' vs. '+compare)

# deaths by date vs deaths by report - big delay here
deaths['Reported'] = state.set_index('Date')['Deaths']
deaths.rolling(7).mean().plot(y=[latest, 'Reported'], title='Date of Death vs. Report (7-day avg)')

        

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

death2 = deaths.reset_index(drop=False)
death2['Date'] = death2['Date'] - datetime.timedelta(days=18)
cases[death_latest] = death2.set_index('Date')[death_latest] / 0.012
cases = cases.reset_index(drop=False)

cases.plot(x='Date', y=[case_latest, 'Cases (reported)'])

cases.plot(x='Date', y=[case_latest, death_latest])



