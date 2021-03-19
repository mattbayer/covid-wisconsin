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

age_weekly = agedata.rolling(7).sum()
age_weekly = age_weekly[age_weekly.index.weekday==6]

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
    
larger = age_weekly.melt(ignore_index=False)
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

cases_age.value = pd.to_numeric(cases_age.value.str.replace(',',''))

count_age = cases_age[cases_age['Count/Rate']=='Count'].drop('Count/Rate', axis=1)
count_age = count_age.pivot(index='Week of', columns='Age group', values = 'value').loc[count_age['Week of'].drop_duplicates(),:]

rate_age = cases_age[cases_age['Count/Rate']=='Rate'].drop('Count/Rate', axis=1)
rate_age = rate_age.pivot(index='Week of', columns='Age group', values = 'value').loc[rate_age['Week of'].drop_duplicates(),:]

share_age = count_age.divide(count_age.sum(axis=1), axis=0)

perc_age = count_age.copy()
# for col in perc_age.columns:
#     perc_age[col] = pd.to_numeric(perc_age[col].str.replace(',',''))


# divide by peak
perc_age = perc_age / perc_age.max()

# divide by certain date
# 65+ first eligible the week of 24-Jan, so start measuring at end of January?
# perc_age = perc_age / perc_age.loc['24-Jan',:]

# divide by average over first 4 weeks of January
# jan = perc_age.loc[['3-Jan','10-Jan','17-Jan','24-Jan'],:]
# perc_age = perc_age / jan.mean()


#%% Plot

colorset = {'<18': 'deepskyblue',
            '18-24': 'green',
            '25-34': 'firebrick',
            '35-44': 'mediumorchid',
            '45-54': 'orangered',
            '55-64': 'darkslategrey',
            '65+': 'gold'}

# get correct order
perc_age = perc_age[colorset.keys()]
share_age = share_age[colorset.keys()]
# limit dates, melt to long format
# plotdata = perc_age.loc['10-Jan':'7-Mar',:].melt(ignore_index=False).reset_index()
plotdata = perc_age.melt(ignore_index=False).reset_index()


# plotdata = rate_age

plotdata = share_age.loc['4-Oct':'7-Mar',:].melt(ignore_index=False).reset_index()



fig = px.line(
    plotdata, 
    x='Week of',
    y='value',
    color='Age group',
    color_discrete_map=colorset,
    title='Share of cases by age group',
    labels={'value': 'Share'}
    )

fig.update_traces(line_width=4,
                  selector=dict(line_color='gold'))
fig.update_layout(yaxis=dict(tickformat=".0%"))

# save as html, with plotly JS library loaded from CDN
htmlfile='docs\\assets\\plotly\\Vaccine-Cases.html'
fig.write_html(
    file=htmlfile,
    default_height=500,
    include_plotlyjs='cdn',
    )   

os.startfile(htmlfile)
