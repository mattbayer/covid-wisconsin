# -*- coding: utf-8 -*-
"""
Work on new plots for monitoring the situation.

Created on Wed Jun 30 10:48:03 2021

@author: 212367548
"""

import pandas as pd
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

#%% Plotly plot for cases / positivity
plotpath = '.\\docs\\assets\\plotly'

# covid.plotly_twolines(
#     pos_df, 
#     'Percent Positive', 
#     'Positive', 
#     plotcolors=['violet', 'steelblue', 'thistle'],
#     secondary_scale=300,
#     savefile=plotpath+'\\Pos-Positivity-WI.html',
#     )

covid.plotly_twolines(
    pos_df, 
    'Reported Cases', 
    'Percent Positive', 
    plotcolors=['steelblue', 'violet', 'lightsteelblue'],
    secondary_scale=1/200,
    range_max=8000,
    savefile=plotpath+'\\Pos-Positivity-WI.html',
    )

covid.plotly_twolines(
    pos_df, 
    'Positive', 
    'Tests', 
    plotcolors=['steelblue', 'olivedrab', 'lightsteelblue'],
    secondary_scale=10,
    range_max=8000,
    savefile=plotpath+'\\Pos-Tests-WI.html',
    )