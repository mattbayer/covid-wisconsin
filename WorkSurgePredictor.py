# -*- coding: utf-8 -*-
"""
Created on Dec 15 09:03:15 2020
Idea for a surge protector 

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



#%% create weekly sums
weekly = state[col_rename.values()]
weekly = weekly.set_index('Date')
weekly = weekly.rolling(7).sum()
weekly = weekly.reset_index()

# sums ending on Monday, i.e. Tuesday-Monday (because Tuesday is when they 
# report results from Monday, so this is results from a Monday-Sunday).
weekly = weekly.loc[weekly.Date.apply(lambda a: a.weekday() == 0)] 
weekly = weekly.reset_index()


weekly['Positivity'] = weekly['Cases'] / weekly['Tests']
# multiply by 1e5 just so it's on same scale as cases/tests
weekly['Pos Index'] = weekly['Positivity'] * 1e5
# arbitrary prevalence measure
weekly['Prevalence Index'] = np.sqrt(weekly['Cases'] * weekly['Positivity']) * 700
weekly.plot(x='Date', y=['Cases', 'Tests', 'Pos Index', 'Prevalence Index'], marker='.')

#%%
quit()

#%% Plot all cases vs. deaths


savefile = '.\\docs\\assets\\plotly\\Surge-Predictor.html'

fig = covid.plotly_twolines(
    state,
    'Positivity',
    'Cases',
    plotcolors=['violet', 'steelblue'],
    secondary_scale=1e4,
    # plotlabels = {'title': 'Surge Detector<br>(assuming CFR '+str(CFR)+'%)',
    #               'yaxis': 'Deaths',
    #               'yaxis_secondary': 'Cases',
    #               },
    column1_bar=True,
    savefile=savefile,
    )    

# # save_png = '.\\docs\\assets\\Cases-Deaths-WI_2020-12-06.png'
# save_png = '.\\docs\\assets\\Cases-Deaths-WI.png'
# fig.write_image(
#     save_png,
#     width=900,
#     height=600,
#     engine='kaleido',
# )
# os.startfile(save_png)


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
CFR_50 = 2.0
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

