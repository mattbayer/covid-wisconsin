# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 12:14:05 2021

@author: matt_
"""

import covid

import pandas as pd
import numpy as np
import plotly.express as px
import datetime
import os

#%% Load NYT data by state

# If I download from my fork
# states_csv = '..\\covid-19-data-nyt\\us-states.csv'
# states_df = pd.read_csv(states_csv)

# Just download right from the original github repository
states_csv_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
states_df = pd.read_csv(states_csv_url)

state_selection = ['Illinois', 'Michigan', 'Minnesota', 'Wisconsin']
population = {'Illinois' : 12.7e6, 
              'Michigan' : 9.99e6, 
              'Minnesota': 5.64e6,
              'Wisconsin': 5.82e6}

selection = states_df[states_df.state.isin(state_selection)].copy()
selection.loc[:,'date'] = pd.to_datetime(selection.date)
selection = selection.rename(columns={'date':'Date', 'state':'State', 'cases':'Cases', 'deaths':'Deaths'})
selection['Cases per million'] = selection.apply(lambda row: row.Cases / population[row.State], axis=1)

# pivot so can do date-based processing
# 7-day average of daily numbers is equal to 7-day diff of cumulative numbers
p = selection.pivot(index='Date', columns='State', values='Cases per million')
p = p.diff(periods=7) 

# Melt to the right format for px.line
plotdata = p.melt(value_name='Cases per million', ignore_index=False).reset_index()

# Limit dates
plotdata = plotdata[plotdata.Date > datetime.datetime(2020, 8, 1)]


#%% Plot

fig = px.line(
    plotdata,
    x='Date',
    y='Cases per million',
    color='State',
    color_discrete_map={'Illinois':'#13294B', 'Michigan':'#FFCB05', 'Minnesota':'#862334', 'Wisconsin':'#C4012F'},
    title='Covid cases for IL/MI/MN/WI<br>(7-day avg., per pop.)'
    )

pngfile = 'docs\\assets\\Cases-Midwest-States.png'
fig.write_image(
    pngfile,
    width=700,
    height=500,
    engine='kaleido',
    )
os.startfile(pngfile)