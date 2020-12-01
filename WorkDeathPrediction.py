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
# deaths delay of 12 weeks (instead of 21) and a CFR of 1.0% (instead of 1.8%).

CFR = 0.010
delay = 12   # days
delay_str = 'Deaths (-'+str(delay)+' days)'

# create delayed death column
deaths = state[['Date', 'Deaths']]
deaths.Date = deaths.Date - datetime.timedelta(days=delay)
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
    plotlabels = {'title': 'WI Cases and Deaths<br>CFR '+str(CFR*100)+'%',
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
    plotlabels = {'title': 'WI Cases over 30 and Deaths<br>CFR (>30) '+str(CFR_30*100)+'%',
                  'yaxis': 'Cases',
                  'yaxis_secondary': 'Deaths',
                  },
    column1_bar=False,
    savefile='.\\docs\\assets\\plotly\\Cases30-Deaths-WI.html',
    )    


#%% Ages

demo_csv = '.\\data\\demographics\\ACSSPP1Y2018.S0201_data_with_overlays_2020-07-21T153630.csv'

demo_data = pd.read_csv(demo_csv).T

# manually pick out the index codes for the age population estimates
age_indices = {'S0201_009E': '<5', 
               'S0201_010E': '5-17', 
               'S0201_011E': '18-24',
               'S0201_012E': '25-34', 
               'S0201_013E': '35-44', 
               'S0201_014E': '45-54', 
               'S0201_015E': '55-64', 
               'S0201_016E': '65-74',
               'S0201_017E': '75+',
               }
pop_age = demo_data.loc[age_indices.keys(), 1]
pop_age = pop_age.rename(age_indices)
pop_age = pd.to_numeric(pop_age)
pop_age = pd.DataFrame(pop_age)
pop_age.columns = ['Percent']

year_span = np.array([5, 13, 7, 10, 10, 10, 10, 10, 10])
pop_age['Year Span'] = year_span
pop_age['Percent per year'] = pop_age['Percent'] / pop_age['Year Span']

pop_age.plot(y='Percent per year', kind='bar')


#%% CDC age ranges
# IFR values from https://www.cdc.gov/coronavirus/2019-ncov/hcp/planning-scenarios.html
cdc_dict = {'0-19': 0.00003,
            '20-49': 0.0002,
            '50-69': 0.005,
            '70+': 0.054,
            }

cdc_ifr = pd.DataFrame(index=cdc_dict.keys(), data=cdc_dict.values(), columns=['IFR'])
cdc_ifr['Pop %'] = 0

cdc_ifr.loc['0-19', 'Pop %']  = (pop_age.loc['<5', 'Percent'] 
                                 + pop_age.loc['5-17', 'Percent'] 
                                 + pop_age.loc['18-24', 'Percent per year'] * 2)
cdc_ifr.loc['20-49', 'Pop %'] = (pop_age.loc['18-24', 'Percent per year'] * 5 
                                 + pop_age.loc['25-34', 'Percent'] 
                                 + pop_age.loc['35-44', 'Percent']
                                 + pop_age.loc['45-54', 'Percent'] / 2)
cdc_ifr.loc['50-69', 'Pop %'] = (pop_age.loc['45-54', 'Percent'] / 2 
                                 + pop_age.loc['55-64', 'Percent'] 
                                 + pop_age.loc['65-74', 'Percent'] / 2)
cdc_ifr.loc['70+', 'Pop %']   = (pop_age.loc['65-74', 'Percent'] / 2 
                                 + pop_age.loc['75+', 'Percent'])

total = state.loc[state.Date == state.Date.max()].iloc[0]   # iloc to make it a Series
cdc_ifr['Cases'] = 0
cdc_ifr.loc['0-19', 'Cases'] = total['POS_0_9'] + total['POS_10_19']
cdc_ifr.loc['20-49', 'Cases'] = total['POS_20_29'] + total['POS_30_39'] + total['POS_40_49']
cdc_ifr.loc['50-69', 'Cases'] = total['POS_50_59'] + total['POS_60_69']
cdc_ifr.loc['70+', 'Cases'] = total['POS_70_79'] + total['POS_80_89'] + total['POS_90']



IFR = (cdc_ifr['IFR'] * cdc_ifr['Pop %'] / 100).sum()
Case_IFR = (cdc_ifr['IFR'] * cdc_ifr['Cases']).sum() / cdc_ifr['Cases'].sum()


