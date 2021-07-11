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
pos_df = pos_df.rename(columns={'Positive': 'Positive tests', 'Percent Positive': 'Percent positive'})

#%% Plotly plot for cases / positivity
plotpath = '.\\docs\\_includes\\plotly'
savefile = plotpath+'\\Cases-Positivity-WI.html'

# covid.plotly_twolines(
#     pos_df, 
#     'Percent Positive', 
#     'Positive', 
#     plotcolors=['darkmagenta', 'steelblue', 'thistle'],
#     secondary_scale=300,
#     savefile=plotpath+'\\Pos-Positivity-WI.html',
#     )

fig = covid.plotly_twolines(
    pos_df, 
    'Positive tests', 
    # 'Reported Cases', 
    'Percent positive',
    plotcolors=['steelblue', 'darkmagenta', 'lightsteelblue'],
    secondary_scale=1/200,
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

fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)


# covid.plotly_twolines(
#     pos_df, 
#     'Positive', 
#     'Tests', 
#     plotcolors=['steelblue', 'olivedrab', 'lightsteelblue'],
#     secondary_scale=10,
#     range_max=8000,
#     savefile=plotpath+'\\Pos-Tests-WI.html',
#     )