# -*- coding: utf-8 -*-
"""
Work on new plots for monitoring the situation.

Created on Wed Jun 30 10:48:03 2021

@author: 212367548
"""

import pandas as pd
import geopandas as gpd
import datetime
from plotly.offline import plot as pplot
import plotly.express as px
import os

import covid

from tableauscraper import TableauScraper as TS
ts = TS()


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
    date_min=datetime.datetime(2021,1,15),
    range_max=2000,
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
# os.startfile(savefile)


