# -*- coding: utf-8 -*-
"""
Work on new plots for monitoring the situation.

Created on Wed Jun 30 10:48:03 2021

@author: 212367548
"""

import pandas as pd
import geopandas as gpd
import datetime
import os
import numpy as np
import plotly.graph_objects as go

import covid

from tableauscraper import TableauScraper as TS
ts = TS()

#%% Cases per 100K max for y-axes
per100k = 250
date_start = datetime.datetime(2021,6,15)

#%% Get positives/tests

pos_df = covid.scrape_widash_postest()

#%% Get reported data and add to pos_df
widata = covid.read_covid_data_wi('state')
pos_df = pos_df.set_index('Date')
pos_df['Reported Cases'] = widata.set_index('Date')['POS_NEW']
pos_df = pos_df.reset_index()
pos_df = pos_df.rename(columns={'Positive': 'Positive tests', 'Percent Positive': 'Percent positive'})

# convert literal percent to proper decimal so interpreted correctly in plot
pos_df['Percent positive'] = pos_df['Percent positive'] / 100

# cut off latest date, misleading data
pos_df = pos_df[pos_df.Date < pos_df.Date.max()]

#%% Plotly plot for cases / positivity
plotpath = '.\\docs\\_includes\\plotly'
savefile = plotpath+'\\Pos-Positivity-WI.html'


fig = covid.plotly_twolines(
    pos_df, 
    'Positive tests', 
    'Percent positive',
    plotcolors=['steelblue', 'darkmagenta', 'lightsteelblue'],
    secondary_scale=1/25000,
    date_min=date_start,
    range_max= per100k * 60,
    col1_mode='avg-bar',
    col2_mode='line',
    plotlabels = {'title': 'WI Positive Tests and Percent Positive',
                  'yaxis': 'Positve tests',
                  'yaxis_secondary': 'Percent positive',
                  },
    savefile=savefile,
    showfig=False,
    )

fig.update_xaxes(title_text='Date of test result')
fig.update_yaxes(secondary_y=True, tickformat=',.0%')
fig.update_traces(secondary_y=True, hovertemplate='%{y:.1%}')

fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)



#%% Map plot for increasing cases


#%% Get the coviddata
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'
csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.download_covid_data_wi('county2')

#%% Geography work

# shapefile from US census - doesn't have lake winnebago which is annoying
shapefile = 'data\\geo\\cb_2019_us_county_500k.shp'
# read data set of all USA counties
countiesUSA = gpd.read_file(shapefile)
# filter on wisconsin
countiesWI = countiesUSA[countiesUSA.STATEFP == '55']

# reindex on county name
countiesWI = countiesWI.set_index('NAME')
# sort by name
countiesWI = countiesWI.sort_index()
# add Population column
countiesWI['Population'] = popdata


#%% Prep county data for map

# reduce and rename columns
col_rename = {'Date': 'Date', 
              'GEOName': 'County', 
              'POS_NEW_CONF': 'Cases',      # confirmed cases
              }

reduced = widata[col_rename.keys()]
reduced = reduced.rename(columns=col_rename)

# convert to date and discard the time portion
reduced.Date = pd.to_datetime(reduced.Date).apply(lambda d: d.date())
reduced = reduced.sort_values('Date')

avg_window = 7
diff_window = 14

# isolate cases
cases = reduced.pivot(index='Date', columns='County', values='Cases')
cases_avg = cases.rolling(window=avg_window, center=False).mean()
currcases = cases_avg.iloc[-1]
pastcases = cases_avg.iloc[-1-diff_window]

# set any negative values to 0
def zeroneg(x):
    if x > 0:
        return x
    else:
        return 0
    
countiesWI['Cases'] = currcases.apply(zeroneg)
countiesWI['Past cases'] = pastcases.apply(zeroneg)

countiesWI['Cases per 100K'] = countiesWI['Cases'] / countiesWI['Population'] * 100000

# get latitude and longitude of centroids of counties for plotting
# this will give warning but I don't care
countiesWI['plotlon'] = countiesWI.geometry.centroid.x
countiesWI['plotlat'] = countiesWI.geometry.centroid.y
# move Milwaukee's plot center to the right a bit to make more room for its bubble
countiesWI.loc['Milwaukee', 'plotlon'] = countiesWI.loc['Milwaukee', 'plotlon'] + 0.07

# append 'County' for display names
display_names = [n + ' County' for n in countiesWI.index]

# set scales for sizes of bubbles
popscale = 300

# cases_size_factor = 
# cases_size_factor = 0.06
cases_size_factor = 0.20 / 40 * per100k

cases_color_range = [0,per100k]



#%% Cases figure
covid.plotly_changebubble(
    countiesWI,
    currcol='Cases',
    pastcol='Past cases',
    colorcol='Cases per 100K',
    size_factor=cases_size_factor,
    color_range=cases_color_range,
    colorscale='Blues',
    location_names=display_names,
    plotlabels=dict(title='Change in Cases by County<br>(7-day avg, 14-day change)', sizelabel='Cases'),
    savefile='.\\docs\\_includes\\plotly\\Map-CaseChange-WI.html',
    fig_height=600,
    showfig=True,
    )




