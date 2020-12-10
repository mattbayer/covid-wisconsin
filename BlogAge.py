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

import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot as pplot

import covid


#%% Age demographic data
demo_csv = '.\\data\\demographics\\ACSST1Y2019.S0101-2020-12-10T154935.csv'

demo_data = pd.read_csv(demo_csv)

pop_age = demo_data.iloc[2:20,0:5]

col_rename = {'Label': 'Age range', 
              'Wisconsin!!Total!!Estimate': 'Population',
              'Wisconsin!!Total!!Margin of Error': 'Population Margin of Error',
              'Wisconsin!!Percent!!Estimate': 'Percent',
              'Wisconsin!!Percent!!Margin of Error': 'Percent Margin of Error',
              }
pop_age = pop_age.rename(columns=col_rename)

# Convert stuff to numeric
# Pop: take out commas and convert from string
pop_age['Population'] = pd.to_numeric(pop_age['Population'].str.replace(',',''))
# Pop margin: take out +/- and commas
pop_age['Population Margin of Error'] = pd.to_numeric(pop_age['Population Margin of Error'].str.replace(',','').str.replace('±', ''))
# Percent: take out %
pop_age['Percent'] = pd.to_numeric(pop_age['Percent'].str.replace('%',''))
# Percent margin: take out +/-
pop_age['Percent Margin of Error'] = pd.to_numeric(pop_age['Percent Margin of Error'].str.replace('±', ''))

pop_age.plot(x='Age range', y='Population', kind='bar')

# Sum ranges to match the Covid data
pop_age_coarse = pop_age[['Population', 'Percent']].rolling(2).sum().iloc[1::2]
age_ranges = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
pop_age_coarse['Age range'] = age_ranges
pop_age_coarse.reset_index(drop=True, inplace=True)

pop_age_coarse.plot(x='Age range', y='Percent', kind='bar')



#%% Parse covid data

state = covid.read_covid_data_wi('state')

covid.plot_by_age(state)

# rename
col_rename = {'Date': 'Date', 'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
state = state.rename(columns=col_rename)

# total
total = state.loc[state.Date == state.Date.max()].iloc[0]   # iloc to make it a Series

age_ranges_covid = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_59', '60_69', '70_79', '80_89', '90']
age_pos   = ['POS_' + s for s in age_ranges_covid]
age_death = ['DTHS_' + s for s in age_ranges_covid]
age_hosp  = ['IP_Y_' + s for s in age_ranges_covid]
age_icu   = ['IC_Y_' + s for s in age_ranges_covid]

age_data = pd.DataFrame(
    data={'Age range': age_ranges_covid,
          'Cases': total[age_pos].to_list(),
          'Hospitalizations': total[age_hosp].to_list(),
          'ICU': total[age_icu].to_list(),
          'Deaths': total[age_death].to_list()},
    )

age_data = age_data.set_index('Age range')

age_perc = age_data / age_data.sum() * 100

age_perc = age_perc.reset_index()
age_data = age_data.reset_index()

#%% Sum up the 80-89 and 90+ rows to match with the demographic data

age_covid = age_data.iloc[0:9, 1:]
age_covid.iloc[8] = age_data.iloc[8:].sum()
age_covid.insert(0, 'Age range', age_ranges)
age_covid.insert(1, 'Population', pop_age_coarse['Population'])
age_covid.insert(2, 'Population %', pop_age_coarse['Percent'])

temp = age_covid[['Cases', 'Hospitalizations', 'ICU', 'Deaths']]
temp_perc = temp / temp.sum() * 100
temp_perc.columns = temp_perc.columns + ' %'

age_covid = age_covid.merge(temp_perc, left_index=True, right_index=True)



#%% Age data plots

# include ICU - interesting for me, take out for blog for brevity
# perc_cols = ['Population %', 'Cases %', 'Hospitalizations %', 'ICU %', 'Deaths %']
# col_colors = ['gray', 'steelblue', 'darkorange', 'darkviolet', 'firebrick']
perc_cols = ['Population %', 'Cases %', 'Hospitalizations %', 'Deaths %']
col_colors = ['gray', 'steelblue', 'darkorange', 'firebrick']

# reformat to "long" for use in the bar graph
age_covid_long = age_covid.melt(id_vars='Age range', value_vars=perc_cols, value_name='Percentage')

# fig = px.bar(
#     age_covid, 
#     x='Age range', 
#     y=['Population %', 'Cases %', 'Hospitalizations %', 'ICU %', 'Deaths %'], 
#     barmode='group',
#     title='WI Covid Data by Age Group',
#     )

# # horizontal layout
# fig = px.bar(
#     age_covid_long, 
#     y='Age range', 
#     x='Percentage', 
#     facet_col='variable', 
#     facet_col_wrap=2,
#     color='variable',
#     color_discrete_sequence=col_colors,
#     orientation='h',
#     category_orders={'Age range': age_ranges},
#     labels={'variable': ''},
#     title='WI Covid Data by Age Group',
#     width=700,
#     height=600,
#     )

# vertical layout
fig = px.bar(
    age_covid_long, 
    x='Age range', 
    y='Percentage', 
    facet_col='variable', 
    facet_col_wrap=2,
    color='variable',
    color_discrete_sequence=col_colors,
    labels={'variable': ''},
    title='WI Covid Data by Age Group',
    width=700,
    height=600,
    )


# take out 'variable=' part of the axis titles
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# other layout
fig.update_layout()

# fig.update_traces(marker_color=['gray', 'steelblue', 'darkorange', 'darkviolet', 'firebrick'])

pplot(fig,
      filename='.\\docs\\assets\\plotly\\Age-Covid.html',
      include_plotlyjs='cdn',
      )

# interesting - ICU admissions are highest for late middle age. Elderly are 
# admitted to ICU lower than proportional to their hospitalization status. I 
# guess because it's less likely to do them any good.

#%% CFR

age_covid['CFR'] = age_covid['Deaths'] / age_covid['Cases']*100
age_covid['Age center'] = range(5,90,10)

# IFR from paper
def ifr(age):
    log_ifr = -3.27 + 0.0524*age
    return 10**log_ifr

age_covid['IFR'] = ifr(age_covid['Age center'])

fig = px.line(
    age_covid, 
    x='Age range', 
    y=['CFR', 'IFR'], 
    log_y=True,
    # line_dash='dash',
    )

fig.update_traces(mode='markers+lines', line_dash='dot')

pplot(fig,
      filename='.\\docs\\assets\\plotly\\Age-CFR.html',
      include_plotlyjs='cdn',
      )

#%% 

ifrlog10 = -3.27 + 0.0524

#%%
quit

#%% Ages - coarser data I had found earlier

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

# pop_age.plot(y='Percent per year', kind='bar')


pop_age['Age bin center'] = [2, 11, 21, 29.5, 39.5, 49.5, 59.5, 69.5, 82]
pop_age['Age bin width']  = pop_age['Year Span']

# fig = px.bar(
#     pop_age, 
#     x='Percent', 
#     y=pop_age.index, 
#     orientation='h', 
#     title='WI Population by Age Group',
#     )


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


cdc_ifr['Cases'] = 0
cdc_ifr.loc['0-19', 'Cases'] = total['POS_0_9'] + total['POS_10_19']
cdc_ifr.loc['20-49', 'Cases'] = total['POS_20_29'] + total['POS_30_39'] + total['POS_40_49']
cdc_ifr.loc['50-69', 'Cases'] = total['POS_50_59'] + total['POS_60_69']
cdc_ifr.loc['70+', 'Cases'] = total['POS_70_79'] + total['POS_80_89'] + total['POS_90']



IFR = (cdc_ifr['IFR'] * cdc_ifr['Pop %'] / 100).sum()
Case_IFR = (cdc_ifr['IFR'] * cdc_ifr['Cases']).sum() / cdc_ifr['Cases'].sum()

# Population weighted IFR is 0.8%.  Case-weighted IFR is 0.65%.


