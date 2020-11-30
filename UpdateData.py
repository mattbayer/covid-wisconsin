# -*- coding: utf-8 -*-
"""
Update Coronavirus data for Wisconsin and make standard plots

Script for downloading, parsing, plotting Covid data from Wisconsin.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

import covid

#%% Update the data

# covid data by county
covid.update_covid_data_wi('state')
covid.update_covid_data_wi('county')

widata = covid.read_covid_data_wi('county')
state = covid.read_covid_data_wi('state')

# population data
datapath = '.\\data'
csv_file_pop = os.path.join(datapath, 'Population-Data-WI.csv')
# covid.download_pop_data_wi(csv_file_pop)
popdata = covid.read_pop_data_wi(csv_file_pop)

#%% Update Dashboard plots
plotpath = '.\\docs\\assets\\plotly'

# reduce and rename at state level
col_rename = {'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
state = state.rename(columns=col_rename)

# Cases / Tests line plot
covid.plotly_casetest(sourcedata=state, 
                      case_col='Cases', 
                      test_col='Tests', 
                      date_col='Date', 
                      savefile=plotpath + '\\Cases-Tests-WI.html',
                      )

# Deaths / Hospitalizations line plot
covid.plotly_deadhosp(sourcedata=state, 
                      hosp_col='Hospitalizations', 
                      dead_col='Deaths', 
                      date_col='Date', 
                      savefile=plotpath + '\\Deaths-Hosp-WI.html',
                      )


# Map plots by importing other script
import UpdateGeo

# Regional plots by importing other script
import BlogRegionalUpdate

#%% Tract work - UWM and Marquette

# # covid data by census tract
# UWM = ['007300', '007400', '007800', '007500']
# Marquette = ['186400', '014600', '014700']


#%% Plot cases and deaths for the state

# use seaborn theme for plotting
# sns.set()

# covid.plot_tests_posrate(widata, 'WI')
# covid.plot_cases_deaths(widata, 'WI')
# covid.plot_cases_tests(widata, 'WI')

#%% Plot deaths, cases, tests

# WI and top 3 counties
# covid.plotDCT(widata, 'WI')
covid.plotDCT(widata, ['WI', 'Milwaukee', 'Dane', 'Brown'], per_capita=True, popdata=popdata)



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




#%% Plot age distribution
# Note - this data is not present for counties.  Only data broken out by 
# county is deaths, cases, tests.
covid.plot_by_age(widata)


# Statement to compute new positives for all counties, before I realized 
# the data wasn't there.  Functions are still useful to learn.
# widata[new_cols] = widata.groupby('NAME')[cumul_cols].diff()


