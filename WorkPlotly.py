# -*- coding: utf-8 -*-
"""
Update Coronavirus data for Wisconsin and make standard plots

Script for downloading, parsing, plotting Covid data from Wisconsin.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import urllib
from scipy import signal
import datetime

import covid


#%% Get the data

# First retrieve data from server and save to csv file
# Second read data from the previously saved csv file
# comment sections if no need to re-download    
datapath = '.\\data'
tractpath = os.path.join(datapath, 'tracts')

csv_file_county = os.path.join(datapath, 'Covid-Data-WI-County.csv')
csv_file_pop = os.path.join(datapath, 'Population-Data-WI.csv')

# population data
# covid.download_pop_data_wi(csv_file_pop)
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data by county
# covid.download_covid_wi_county()
widata = covid.read_covid_data_wi(dataset='county')





#%% Plotly

import plotly
import plotly.express as px
from plotly.offline import plot as pplot
import plotly.graph_objects as go


# filter to state
state = widata[widata.NAME == 'WI']
# index and sort by date
state = state.set_index('Date')
state = state.sort_index()
# state = state.sort_values('Date')

# create new hosp column
state = state.assign(HOSP_NEW = state.HOSP_YES.diff(periods=1))

# reduce and rename columns
col_rename = {'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
col_cumul = {'POSITIVE': 'Total Cases', 'NEGATIVE': 'Total Negative', 'HOSP_YES': 'Total Hospitalizations', 'DEATHS': 'Total Deaths'}
state = state[col_rename.keys()]
state = state.rename(columns=col_rename)

# rolling 7-day average
state_avg = state.rolling(window=7, center=False).mean()


# create one-axis plot
# fig = px.line(state_avg, y='Cases', title='WI Cases/Tests 7-day avg')

# # pplot(fig, filename='..\\mattbayer.github.io\\assets\\plotly\\Cases_WI_2020-09-28.html')

# pplot(fig, filename='.\\plots\\plotly\\temp.html')

#%% Standard plots
plotpath = '..\\mattbayer.github.io\\assets\\plotly'

# Cases/Tests

# compute y axis range
# want tests to be on a scale exactly 10x cases
range_max = max(state_avg.Tests.max()/10, state_avg.Cases.max())
range_cases = np.array([-range_max * 0.05, 1.05*range_max])


fig = plotly.subplots.make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(x=state_avg.index, 
               y=state_avg.Cases, 
               name='Cases (7-day avg)', 
               line_color='steelblue', 
               hovertemplate='%{y:.0f}'),
    secondary_y=False)

fig.add_trace(
    go.Scatter(x=state_avg.index, 
               y=state_avg.Tests, 
               name='Tests (7-day avg)', 
               line_color='olivedrab', 
               hovertemplate='%{y:.0f}'),
    secondary_y=True)


fig.update_yaxes({'range': range_cases}, secondary_y=False, title_text='Daily cases')
fig.update_yaxes({'range': range_cases*10}, secondary_y=True, title_text='Daily new people tested')
fig.update_layout(title_text='WI Daily Cases and Tests',
                  hovermode='x unified',
                  legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))                
                

pplot(fig, filename = plotpath + '\\Cases-Tests-WI.html')


#%% Hospitalizations / Deaths

hosp_death_factor = 1

range_max = max(state_avg.Deaths.max(), state_avg.Hospitalizations.max()/hosp_death_factor)
range_deaths = np.array([-range_max * 0.05, 1.05*range_max])

fig = plotly.subplots.make_subplots()

fig.add_trace(
    go.Bar(x=state.index, 
           y=state.Deaths,
           name='Deaths', 
           marker_color='firebrick', 
           hovertemplate='%{y:.0f}'),)

fig.add_trace(
    go.Scatter(x=state_avg.index, 
               y=state_avg.Hospitalizations, 
               name='Hospitalizations (7-day avg)', 
               line_color='darkorange', 
               hovertemplate='%{y:.1f}'),)


fig.update_yaxes({'range': range_deaths}, secondary_y=False, title_text='Daily deaths / hospitalizations')
fig.update_yaxes({'range': range_deaths*hosp_death_factor}, secondary_y=True, title_text='Daily hospitalizations')
fig.update_layout(title_text='WI Daily Deaths and Hospitalizations',
                  hovermode='x unified',
                  legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

# fig.add_annotation(dict(text='*Deaths are daily reported values, Hospitalizations are 7-day averages.',
#                         x=0.05, y=-0.1, 
#                         xref='paper', yref='paper',
#                         showarrow=False))

pplot(fig, filename = plotpath + '\\Deaths-Hosp-WI.html')

