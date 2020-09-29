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

# covid data by census tract
UWM = ['007300', '007400', '007800', '007500']
Marquette = ['186400', '014600', '014700']
# covid.download_covid_wi_tract(UWM + Marquette, tractpath)
# data = covid.read_covid_data_wi(data_path='.\\data\\tracts', csv_file='Covid-Data-WI-Tract-007300.csv')

# update ALL data at once
# covid.update_covid_wi_all(datapath)




#%% Plot deaths, cases, tests

# WI and top 3 counties
covid.plotDCT(widata, 'WI')
covid.plotDCT(widata, ['WI', 'Milwaukee', 'Dane', 'Brown'], per_capita=True, popdata=popdata)


# covid.plotDCT(widata, ['WI', 'Milwaukee', 'Sheboygan', 'Brown', 'Dane', 'La Crosse'], per_capita=True, popdata=popdata)


#%% Plot by county

covid.plot_by_county(widata, popdata, 'POS_NEW', 9)
# covid.plot_by_county(widata, popdata, 'DTH_NEW', 6)

#%% Various groups of counties, cases and pos rate

# Current hot spots - sort by per-capita new cases
pivot = widata.pivot(index='Date', columns='NAME', values='POS_NEW')
avg = pivot.rolling(window=7, center=False).mean()
capita = covid.convert_per_capita(avg, popdata)
counties = capita.columns
last_value = capita.iloc[-1]
sort_order = last_value.sort_values(ascending=False)

hotspots = sort_order.index[0:8].insert(0,'WI')
covid.plot_cases_posrate(widata, hotspots, per_capita=True, popdata=popdata)
plt.suptitle('Hotspots')

# Sort counties by population
popcounties = popdata.sort_values(ascending=False).head(9).index
covid.plot_cases_posrate(widata, popcounties, per_capita=True, popdata=popdata)


# Milwaukee area
covid.plot_cases_posrate(widata, ['WI', 'Milwaukee', 'Waukesha', 'Kenosha', 'Racine', 'Washington'], per_capita=True, popdata=popdata)
plt.suptitle('Milwaukee area')




#%% Plotly

import plotly.express as px
from plotly.offline import plot as pxplot

# filter to state
state = widata[widata.NAME == 'WI']
# index and sort by date
state = state.set_index('Date')
state = state.sort_index()
# state = state.sort_values('Date')

# create new hosp column
state = state.assign(HOSP_NEW = state.HOSP_YES.diff(periods=1))

# reduce and rename columns
col_rename = {'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalized'}
col_cumul = {'POSITIVE': 'Total Cases', 'NEGATIVE': 'Total Negative', 'HOSP_YES': 'Total Hospitalized', 'DEATHS': 'Total Deaths'}
state = state[col_rename.keys()]
state = state.rename(columns=col_rename)

# rolling 7-day average
state_avg = state.rolling(window=7, center=True).mean()


# # Create plot

# import plotly.graph_objects as go
# from plotly.subplots import make_subplots

# # Create figure with secondary y-axis
# fig = make_subplots(specs=[[{"secondary_y": True}]])

# # Add traces
# fig.add_trace(
#     go.Scatter(x=[1, 2, 3], y=[40, 50, 60], name="yaxis data"),
#     secondary_y=False,
# )

# fig.add_trace(
#     go.Scatter(x=[2, 3, 4], y=[4, 5, 6], name="yaxis2 data"),
#     secondary_y=True,
# )

# # Add figure title
# fig.update_layout(
#     title_text="Double Y Axis Example"
# )

# # Set x-axis title
# fig.update_xaxes(title_text="xaxis title")

# # Set y-axes titles
# fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
# fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

# fig.show()

# create plot
fig = px.line(state_avg, y=['Cases', 'Tests'], title='WI Cases/Tests 7-day avg')

# pxplot(fig, filename='..\\mattbayer.github.io\\assets\\plotly\\Cases_WI_2020-09-28.html')

pxplot(fig, filename='.\\plots\\plotly\\temp.html')
