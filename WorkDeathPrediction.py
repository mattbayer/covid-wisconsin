# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 09:03:15 2020

@author: Matt Bayer
"""



import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

import covid

#%% Load data

state = covid.read_covid_data_wi('state')

# rename
col_rename = {'Date': 'Date', 'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
state = state.rename(columns=col_rename)




#%% Plot deaths vs cases
# contra Trevor Bedford on the national data - this seems to fit better with a 
# deaths delay of 2 weeks (instead of 3) and a CFR of 1.1% (instead of 1.8%).

CFR = 0.011
delay = 2   # weeks
delay_str = 'Deaths (-'+str(delay)+' weeks)'

# create delayed death column
deaths = state[['Date', 'Deaths']]
deaths.Date = deaths.Date - datetime.timedelta(days=delay*7)
deaths = deaths.set_index('Date')
state = state.set_index('Date')
state[delay_str] = deaths
state = state.reset_index()



savefile = '.\\docs\\assets\\plotly\\Cases-Deaths-WI.html'

fig = covid.plotly_twolines(
    state,
    'Cases',
    delay_str,
    plotcolors=['steelblue', 'firebrick'],
    secondary_scale=CFR,
    plotlabels = {'title': 'WI Cases and Deaths',
                  'yaxis': 'Cases',
                  'yaxis_secondary': 'Deaths',
                  },
    column1_bar=False,
    savefile=savefile,
    )    


#%% Compile over-30 data

over30 = ['POS_30_39', 'POS_40_49', 'POS_50_59', 'POS_60_69', 'POS_70_79', 'POS_80_89', 'POS_90']
under30 = ['POS_0_9', 'POS_10_19', 'POS_20_29']

state['Cases over 30'] = state[over30].sum(axis=1).diff()
state['Cases under 30'] = state[under30].sum(axis=1).diff()

fig = covid.plotly_twolines(
    state,
    'Cases',
    'Cases over 30',
    plotcolors=['steelblue', 'rebeccapurple'],
    # secondary_scale=CFR,
    plotlabels = {'title': 'WI Cases and Deaths',
                  'yaxis': 'Cases',
                  # 'yaxis_secondary': 'Deaths',
                  },
    column1_bar=False,
    savefile='.\\docs\\assets\\plotly\\Cases-Cases30-WI.html',
    )  

#%% Cases over 30 vs deaths

CFR_30 = 0.015
fig = covid.plotly_twolines(
    state,
    'Cases over 30',
    delay_str,
    plotcolors=['rebeccapurple', 'firebrick'],
    secondary_scale=CFR_30,
    plotlabels = {'title': 'WI Cases over 40 and Deaths',
                  'yaxis': 'Cases',
                  'yaxis_secondary': 'Deaths',
                  },
    column1_bar=False,
    savefile='.\\docs\\assets\\plotly\\Cases30-Deaths-WI.html',
    )    