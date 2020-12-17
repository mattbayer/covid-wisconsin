# -*- coding: utf-8 -*-
"""
Created on Dec 17 2020

1. Thanksgiving surge?
2. Deaths vs cases update

@author: Matt Bayer
"""



import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import datetime

import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot as pplot
plotpath = '.\\docs\\assets\\plotly'

import covid

#%% Load data

state = covid.read_covid_data_wi('state')

# rename
col_rename = {'Date': 'Date', 'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
state = state.rename(columns=col_rename)

# tests by result date
tests = covid.read_bytest_wi("data\\By_Test_Data_data_2020-12-17.csv")


#%% Process tests by result date

tests['Tests 7-day'] = tests['Tests'].rolling(7).mean()
tests['Positives 7-day'] = tests['Positives'].rolling(7).mean()
tests['Positivity 7-day'] = tests['Positives 7-day'] / tests['Tests 7-day']
tests['Positivity'] = tests['Positives'] / tests['Tests']
tests['Positivity 7-day x10000'] = tests['Positivity 7-day'] * 10000
tests['Prevalence Index'] = np.sqrt(tests['Positives 7-day'] * tests['Positivity 7-day']) * 200

tests['Weekday'] = tests.Date.apply(lambda d: d.weekday())

tests.plot(x='Date', y=['Positives 7-day', 'Positivity 7-day x10000', 'Prevalence Index'])

fig = px.bar(tests, x='Date', y=['Positives', 'Tests'], barmode='group')
pplot(fig, include_plotlyjs='cdn', filename=plotpath+'\\temp.html')

fig = px.line(tests, x='Date', y='Positives', color='Weekday')
pplot(fig, include_plotlyjs='cdn', filename=plotpath+'\\temp.html')

#%% Plot tests by result date



covid.plotly_twolines(
    tests, 
    'Positivity', 
    'Positives', 
    plotcolors=['violet', 'steelblue'],
    secondary_scale=1e4,
    )

covid.plotly_casetest(sourcedata=tests, 
                      case_col='Positives', 
                      test_col='Tests', 
                      date_col='Date', 
                      savefile=plotpath + '\\Pos-Test-ByResult-WI.html',
                      )


#%% Plot deaths vs cases
# contra Trevor Bedford on the national data - this seems to fit better with a 
# deaths delay of 12 days (instead of 21) and a CFR of 1.0% (instead of 1.8%).
delay = 12
CFR = 1.0

def create_delayed_deaths(state, delay):
    # create delayed death column
    deaths = state[['Date', 'Deaths']]
    deaths.Date = deaths.Date - datetime.timedelta(days=delay)
    deaths = deaths.set_index('Date')
    state = state.set_index('Date')
    delay_str = 'Deaths (-'+str(delay)+' days)'
    state[delay_str] = deaths
    state = state.reset_index()
    return state, delay_str


state, delay_str = create_delayed_deaths(state, delay)


#%% Plot all cases vs. deaths

savefile = '.\\docs\\assets\\plotly\\Cases-Deaths-WI.html'

fig = covid.plotly_twolines(
    state,
    delay_str,
    'Cases',
    plotcolors=['firebrick', 'steelblue', 'rosybrown'],
    secondary_scale=1/(CFR/100),
    plotlabels = {'title': 'WI Deaths and Cases<br>(assuming CFR '+str(CFR)+'%)',
                  'yaxis': 'Deaths',
                  'yaxis_secondary': 'Cases',
                  },
    column1_bar=True,
    savefile=savefile,
    )    

# save_png = '.\\docs\\assets\\Cases-Deaths-WI_2020-12-06.png'
save_png = '.\\docs\\assets\\Cases-Deaths-WI.png'
fig.write_image(
    save_png,
    width=900,
    height=600,
    engine='kaleido',
)
os.startfile(save_png)


