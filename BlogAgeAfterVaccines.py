# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 10:28:40 2021

@author: 212367548
"""

import covid

import pandas as pd
import numpy as np
import plotly.express as px

#%% Get data and smooth

state = covid.read_covid_data_wi('state')
agedata = covid.new_by_age_wi(state)

data_types = ['Cases', 'Hospitalizations', 'Deaths']

# first 7-day boxcar average for weekly effects, 
# then 5-day hamming to smooth more
age_smooth = agedata.rolling(14).mean()
age_smooth = age_smooth.rolling(window=5, win_type='hamming').mean()

# sum up larger age brackets
def larger_brackets(age_min):
    if age_min < 30:
        return '0-29'
    elif age_min < 60:
        return '30-59'
    # elif age_min < 80:
    #     return '60-79'
    # else:
    #     return '80+'
    else:
        return '60+'
    
larger = age_smooth.melt(ignore_index=False)
larger['Larger bracket'] = larger['Age bracket min'].apply(larger_brackets)
larger = larger.groupby(['Date', 'Data type', 'Larger bracket']).sum()
larger = larger.drop(columns='Age bracket min')
larger = larger.reset_index()
# take out 0-29, it just confuses the plots
# larger = larger[larger['Larger bracket'] != '0-29']
# re-pivot for plotting
larger = larger.pivot(index='Date', columns=['Data type', 'Larger bracket'], values='value')

# percentage from max
age_bymax = larger / larger.max()


# plot

for dtype in data_types:
    age_bymax[dtype].plot(title=dtype)