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

covid.plot_by_age(state)

# rename
col_rename = {'Date': 'Date', 'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
state = state.rename(columns=col_rename)




#%% Plot deaths vs cases
# contra Trevor Bedford on the national data - this seems to fit better with a 
# deaths delay of 12 days (instead of 21) and a CFR of 1.0% (instead of 1.8%).

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


# Compile over-30 data
over30 = ['POS_30_39', 'POS_40_49', 'POS_50_59', 'POS_60_69', 'POS_70_79', 'POS_80_89', 'POS_90']
under30 = ['POS_0_9', 'POS_10_19', 'POS_20_29']

state['Cases over 30'] = state[over30].sum(axis=1).diff()
state['Cases under 30'] = state[under30].sum(axis=1).diff()

# Compile over-50 data
over50 = ['POS_50_59', 'POS_60_69', 'POS_70_79', 'POS_80_89', 'POS_90']
under50 = ['POS_0_9', 'POS_10_19', 'POS_20_29', 'POS_30_39', 'POS_40_49']

state['Cases over 50'] = state[over50].sum(axis=1).diff()
state['Cases under 50'] = state[under50].sum(axis=1).diff()


#%% Plot all cases vs. deaths
CFR = 1.0
state, delay_str = create_delayed_deaths(state, delay=12)

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


#%% Plot cases vs cases-30
if False:
    fig = covid.plotly_twolines(
        state,
        'Cases',
        'Cases over 30',
        plotcolors=['steelblue', 'rebeccapurple'],
        # secondary_scale=CFR,
        plotlabels = {'title': 'WI Cases and Cases over 30',
                      'yaxis': 'Cases',
                      # 'yaxis_secondary': 'Deaths',
                      },
        column1_bar=False,
        savefile='.\\docs\\assets\\plotly\\Cases-Cases30-WI.html',
        )  

#%% Cases over 30 vs deaths
CFR_30 = 1.4

fig = covid.plotly_twolines(
    state,
    delay_str,
   'Cases over 30',
    plotcolors=['firebrick', 'rebeccapurple', 'rosybrown'],
    secondary_scale=1/(CFR_30/100),
    plotlabels = {'title': 'WI Deaths and Cases over 30yr<br>(Assume CFR '+str(CFR_30)+'% for >30yr)',
                  'yaxis': 'Deaths',
                  'yaxis_secondary': 'Cases',
                  },
    column1_bar=True,
    savefile='.\\docs\\assets\\plotly\\Cases30-Deaths-WI.html',
    )    

#%% Cases over 50 vs deaths
# interesting, actually doesn't work that well
CFR_50 = 2.5
state, delay_str = create_delayed_deaths(state, delay=12)

fig = covid.plotly_twolines(
    state,
    delay_str,
   'Cases over 50',
    plotcolors=['firebrick', 'rebeccapurple', 'rosybrown'],
    secondary_scale=1/(CFR_50/100),
    plotlabels = {'title': 'WI Deaths and Cases over 50yr<br>(Assume CFR '+str(CFR_50)+'% for >50yr)',
                  'yaxis': 'Deaths',
                  'yaxis_secondary': 'Cases',
                  },
    column1_bar=True,
    savefile='.\\docs\\assets\\plotly\\Cases50-Deaths-WI.html',
    )    





#%% Compare with deaths by death date

def read_death_raw(death_file):
    death_raw = pd.read_csv(death_file)
    # Note: key is to download the file and then re-save it in Excel specifically
    # as csv, otherwise it's actually tab delimited and harder to read in in python
    
    death = death_raw.iloc[:,2:]
    death = death.rename(columns={'Unnamed: 2': 'series'})
    death.iloc[0,0] = 'Date'
    death = death.set_index('series').T.reset_index(drop=True)
    death.columns.name = ''
    
    death['Date'] = pd.to_datetime(death['Date']+'-2020')
    
    death = death.set_index('Date')
    
    return death

death_03 = read_death_raw('.\\data\\Deaths by day stacked_2020-12-03.csv')
death_04 = read_death_raw('.\\data\\Deaths by day stacked_2020-12-04.csv')
death_10 = read_death_raw('.\\data\\Deaths by day stacked_2020-12-10.csv')

death = death_10
death['Deaths 3-Dec'] = pd.to_numeric(death_03['Confirm + Probable deaths'])
death['Deaths 4-Dec'] = pd.to_numeric(death_04['Confirm + Probable deaths'])
death['Deaths 10-Dec'] = pd.to_numeric(death_10['Confirm + Probable deaths'])
death['Deaths (reported)'] = state.set_index('Date')['Deaths']

# compare = 'Deaths 4-Dec'
compare = 'Deaths 10-Dec'

death.plot(y=[compare, 'Deaths (reported)'])
death['Difference'] = death[compare] - death['Deaths 3-Dec']
death.plot(y=['Deaths 3-Dec', compare, 'Difference'])


# seems like a huge delay in deaths... but if there is such a big delay, then
# I can't trust the deaths-by-date curve right now either, and you would have
# to expect continued large numbers of reports coming in for past days.

