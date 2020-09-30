# -*- coding: utf-8 -*-
"""
Work on positivity rate

Comparing positivity rate for new persons, vs. all tests
"""
# path = 'C:/dev/Covid/'
path = './'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import covid
import urllib
from scipy import signal
import datetime

import geopandas as gpd


#%% Get the coviddata
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'
csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.read_covid_data_wi()


#%% Geography work

# WI DNR shapefile - doesn't have lake winnebago either, so never mind
# shapefile = 'data\\geo\\WI_County_Boundaries_24K.shp'
# countiesWI = gpd.read_file(shapefile)
# countiesWI['NAME'] = countiesWI.COUNTY_NAM

# shapefile from US census - doesn't have lake winnebago which is annoying
shapefile = 'data\\geo\\cb_2019_us_county_500k.shp'
# read data set of all USA counties
countiesUSA = gpd.read_file(shapefile)
# filter on wisconsin
countiesWI = countiesUSA[countiesUSA.STATEFP == '55']


#%% 
# reindex on county name
countiesWI = countiesWI.set_index('NAME')
# sort by name
countiesWI = countiesWI.sort_index()
# add Population column
countiesWI['Population'] = popdata

# chloropleth by population
base = countiesWI.plot(column='Population', edgecolor='w', linewidth=0.5)


#%%

# create new hospitalizations column; need to sort by date first
widata = widata.sort_values('Date')
widata = widata.assign(HOSP_NEW = widata.groupby('NAME').HOSP_YES.diff(periods=1))

# reduce and rename columns
col_rename = {'Date': 'Date', 'NAME': 'County', 'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
reduced = widata[col_rename.keys()]
reduced = reduced.rename(columns=col_rename)

# 7-day rolling average
# reset_index() at end to take result back to original format, instead of counties as a MultiIndex
# reduced_avg = reduced.groupby('County').rolling(window=7, on='Date', center=False).mean().reset_index(level=0)
# last_avg = reduced_avg[reduced_avg.Date == reduced_avg.Date.max()]
# not working...something wrong here.

avg_window = 7

# isolate cases
cases = reduced.pivot(index='Date', columns='County', values='Cases')
cases_avg = cases.rolling(window=avg_window, center=False).mean()
cases_for_map = cases_avg.iloc[-1]

countiesWI['Cases'] = cases_for_map
countiesWI['Cases per 100,000'] = countiesWI['Cases'] / countiesWI['Population'] * 100000

# hospitalizations
hosp = reduced.pivot(index='Date', columns='County', values='Hospitalizations')
hosp_avg = hosp.rolling(window=avg_window, center=False).mean()
hosp_for_map = hosp_avg.iloc[-1]

countiesWI['Hospitalizations'] = hosp_for_map
countiesWI['Hospitalizations per 100,000'] = countiesWI['Hospitalizations'] / countiesWI['Population'] * 100000



#%% Plotly
import json
import plotly.express as px
from plotly.offline import plot as pplot

plotcol = 'Cases per 100,000'
plotcol2 = 'Hospitalizations per 100,000'

# with urllib.request.urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    
# filter counties shapefile to WI, convert to JSON format string, then decode 
# to dictionary with json.loads()
# countiesJS = json.loads(countiesUSA[countiesUSA.STATEFP == '55'].to_json())
countiesJS = json.loads(countiesWI.to_json())

fig = px.choropleth(countiesWI, 
                    geojson=countiesJS, 
                    locations=countiesWI.index, 
                    color=plotcol, 
                    color_continuous_scale=px.colors.sequential.Blues,
                    title='Cases by County',
                    projection='mercator')
fig.update_geos(fitbounds='locations', visible=False)

pplot(fig, filename='.\\plots\\plotly\\temp.html' )

fig2 = px.choropleth(countiesWI, 
                    geojson=countiesJS, 
                    locations=countiesWI.index, 
                    color=plotcol2, 
                    color_continuous_scale=px.colors.sequential.Oranges,
                    title='Hospitalizations by County',
                    projection='mercator')
fig2.update_geos(fitbounds='locations', visible=False)


pplot(fig2, filename='.\\plots\\plotly\\temp2.html' )




