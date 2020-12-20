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



#%% Thanksgiving surge for Milwaukee

# get milwaukee test numbers by copying html of the dashboard and scraping it
# get this originally by doing a browser html inspection of the graph on the Milwaukee county dashboard,
# then copying it to a text file.  The tooltips of the graph are stored in "aria-label" labels, so
# I can regex on these labels below.



# mketests = covid.read_dashboard_mke('C:\dev\covid-wisconsin\data\Dashboard-Milwaukee-Tests_2020-11-09.html', 'Tests')
# mkecases = covid.read_dashboard_mke('C:\dev\covid-wisconsin\data\Dashboard-Milwaukee-Cases_2020-11-09.html', 'Cases')
# mke = mketests.merge(mkecases)
# mke['Positive Rate'] = mke.Cases / mke.Tests

# mke.plot(x='Date', y=['Tests', 'Cases'])
# mke.plot(x='Date', y='Positive Rate')

# mkecases2 = covid.read_dashboard_mke('C:\dev\covid-wisconsin\data\Dashboard-Milwaukee-Cases_2020-12-17.html')

#%%

html_cases = 'C:\dev\covid-wisconsin\data\Dashboard-Milwaukee-Cases_2020-12-17.html'
html_tests = 'C:\dev\covid-wisconsin\data\Dashboard-Milwaukee-Tests_2020-12-17.html'
html_file2 = 'C:\dev\covid-wisconsin\data\Dashboard-Milwaukee-Cases_2020-11-09.html'

# file_obj = open(html_file)
# file_text = file_obj.read()

# m = re.findall('aria-label=\"(.*?)(\d+/\d+)(.*?)\"', file_text)

mke_case = covid.read_dashboard_mke(html_cases)
mke_test = covid.read_dashboard_mke(html_tests)
mke_test = mke_test.replace(to_replace='7 Day Average', value='Tests 7-day')

mke = mke_case.append(mke_test)
mke = mke.pivot(index='Date', columns='variable', values='value')
mke = mke.reset_index()

mke['Weekday'] = mke['Date'].apply(lambda d: d.weekday())
mke['Positivity'] = mke['Cases'] / mke['Tests']

# sum weekly Mon-Sun
# sum with a rolling weekly window, then keep the results from Sunday
weekly = mke[['Cases', 'Tests']].rolling(7).sum()
weekly['Date'] = mke['Date']
weekly = weekly.loc[mke['Weekday'] == 6]

# sum weekly Mon-Wed only
# sum with a rolling 3-day window, then keep the results from Wednesday
monwed = mke[['Cases', 'Tests']].rolling(3).sum()
monwed['Date'] = mke['Date']
monwed = monwed.loc[mke['Weekday'] == 2]
monwed['Positivity'] = monwed['Cases'] / monwed['Tests']


weekly['Positivity'] = weekly['Cases'] / weekly['Tests']

weekly.plot(x='Date', y='Positivity', marker='.')
#%% Overlap bar plot
if False:
    
    fig = px.bar(mke.loc[mke['Date'] >= datetime.datetime(2020,11,9)], 
                 x='Date', y=['Tests', 'Cases'], barmode='overlay', 
                 color_discrete_sequence=['olivedrab','navy'], opacity=0.8)
    
    
    
    # add dividers
    date = datetime.datetime(2020,11,15,12)
    delta = datetime.timedelta(days=7)
    dividers = list()
    for d in range(0,4):
        dividers.append(
            dict(
                type= 'line', line_color='gray', line_dash='dot',
                yref= 'paper', y0= 0, y1= 1,
                xref= 'x', x0=date, x1=date
            )
        )
        date = date + delta
    
    fig.update_layout(shapes=dividers)
    fig.add_annotation(x=datetime.datetime(2020,11,25,22), y=1000, yanchor='bottom', xanchor='center', 
                       showarrow=False,
                       text='Thanksgiving', textangle=270)
    
    pplot(fig, include_plotlyjs='cdn', filename=plotpath+'\\temp.html')

#%% facet bar plot?

temp = mke.loc[mke['Date'] >= datetime.datetime(2020,11,9)]
temp = temp[['Date', 'Cases', 'Tests']].melt(id_vars='Date')

fig = px.bar(
    temp, 
    x='Date', 
    y='value', 
    facet_row='variable',
    color='variable',
    color_discrete_sequence=['steelblue', 'olivedrab'],    
    title='Thanksgiving Milwaukee',
    width=700,
    height=500,
    )

fig.for_each_annotation(lambda a: a.update(text=''))
fig.update_layout(showlegend=False)
fig.update_yaxes(matches=None)
fig.update_yaxes(title='Cases')
fig.update_yaxes(title='Tests', row=1)


# add dividers
date = datetime.datetime(2020,11,15,12)
delta = datetime.timedelta(days=7)
dividers = list()
for d in range(0,4):
    dividers.append(
        dict(
            type= 'line', line_color='gray', line_dash='dot',
            yref= 'paper', y0= 0, y1= 1,
            xref= 'x', x0=date, x1=date
        )
    )
    date = date + delta

fig.update_layout(shapes=dividers)
fig.add_annotation(text='Thanksgiving',
                   x=datetime.datetime(2020,11,25,22), 
                   y=1000, 
                   yanchor='bottom', xanchor='center', showarrow=False, textangle=270)
                   
fig.add_annotation(text='Thanksgiving',
                   x=datetime.datetime(2020,11,25,22), 
                   y=150, row=0, col=0,
                   yanchor='bottom', xanchor='center', showarrow=False, textangle=270)

pplot(fig, include_plotlyjs='cdn', filename=plotpath+'\\temp.html')


#%%
fig = px.bar(weekly, x='Date', y=['Cases', 'Tests'], barmode='group')
pplot(fig, include_plotlyjs='cdn', filename=plotpath+'\\temp.html')

fig = px.line(weekly, x='Date', y=['Cases', 'Tests'])
fig.update_traces(mode='markers', marker_size=10)
pplot(fig, include_plotlyjs='cdn', filename=plotpath+'\\temp.html')


    
    
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


