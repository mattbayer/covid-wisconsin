# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 10:28:40 2021

@author: 212367548
"""

import covid

import pandas as pd
import numpy as np
import plotly.express as px
import os

#%% Get data and smooth

state = covid.read_covid_data_wi('state')
agedata = covid.new_by_age_wi(state)

data_types = ['Cases', 'Hospitalizations', 'Deaths']

# first 7-day boxcar average for weekly effects, 
# then 5-day hamming to smooth more
age_smooth = agedata.rolling(14).mean()
age_smooth = age_smooth.rolling(window=5, win_type='hamming').mean()

# sum up larger age brackets
def larger_brackets(age_min):
    if age_min < 30:
        return '0-29'
    elif age_min < 60:
        return '30-59'
    # elif age_min < 80:
    #     return '60-79'
    # else:
    #     return '80+'
    else:
        return '60+'
    
larger = age_smooth.melt(ignore_index=False)
larger['Larger bracket'] = larger['Age bracket min'].apply(larger_brackets)
larger = larger.groupby(['Date', 'Data type', 'Larger bracket']).sum()
larger = larger.drop(columns='Age bracket min')
larger = larger.reset_index()
# take out 0-29, it just confuses the plots
# larger = larger[larger['Larger bracket'] != '0-29']
# re-pivot for plotting
larger = larger.pivot(index='Date', columns=['Data type', 'Larger bracket'], values='value')

# percentage from max
age_bymax = larger / larger.max()


# plot

for dtype in data_types:
    age_bymax[dtype].plot(title=dtype)
    
    
#%% Cases by age data

cases_age_file = 'data\\Cases-by-age-weekly_2021-03-12.csv'
cases_age = pd.read_csv(cases_age_file)
cases_age.columns = cases_age.loc[0,:]
cases_age = cases_age.loc[1:,:]
as_of = cases_age.loc[1, 'Day of DATE']
cases_age = cases_age.drop(['Day of DATE', 'Measure toggle for title'], axis=1)
cases_age = cases_age.rename(
    columns = {np.nan:'Count/Rate',
               'New Age Groups': 'Age group',
               })
cases_age = cases_age[cases_age['Count/Rate'] != 'Measure toggle']
cases_age = cases_age.melt(id_vars=['Age group', 'Count/Rate'])
cases_age = cases_age.rename(columns = {0: 'Week of'})
cases_age.loc[cases_age['Count/Rate']=='Distinct count of Incident ID', 'Count/Rate'] = 'Count'
cases_age.loc[cases_age['Count/Rate']=='case rate by age for 100K ', 'Count/Rate'] = 'Rate'

count_age = cases_age[cases_age['Count/Rate']=='Count'].drop('Count/Rate', axis=1)
rate_age = cases_age[cases_age['Count/Rate']=='Rate'].drop('Count/Rate', axis=1)

perc_age = count_age.pivot(index='Week of',columns='Age group', values='value').loc[count_age['Week of'].drop_duplicates(),:]
for col in perc_age.columns:
    perc_age[col] = pd.to_numeric(perc_age[col].str.replace(',',''))


# divide by peak
perc_age = perc_age / perc_age.max()


#%% Plot

# divide by certain date
# 65+ first eligible the week of 24-Jan, so start measuring at end of January?
perc_age = perc_age / perc_age.loc['7-Feb',:]
plotdata = perc_age.melt(ignore_index=False).reset_index()

# plotdata = rate_age


fig = px.line(
    plotdata, 
    x='Week of',
    y='value',
    color='Age group',
    # color_discrete_sequence=['orange', 'lightsteelblue'],
    title='Cases by age group',
    # labels={'index':'Date', 'value': 'Cases / day'}
    )

# save as html, with plotly JS library loaded from CDN
htmlfile='docs\\assets\\plotly\\Vaccine-Cases.html'
fig.write_html(
    file=htmlfile,
    default_height=500,
    include_plotlyjs='cdn',
    )   

os.startfile(htmlfile)
