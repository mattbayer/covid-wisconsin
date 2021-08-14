# -*- coding: utf-8 -*-
"""
Work on new plots for monitoring the situation.

Created on Wed Jun 30 10:48:03 2021

@author: 212367548
"""

import pandas as pd
import geopandas as gpd
import datetime
from plotly.offline import plot as pplot
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

import covid

from tableauscraper import TableauScraper as TS
ts = TS()



#%% Plot delay between cases and deaths

# parameters for comparison
lag = 12
cfr = 0.013

# Positives by test date and deaths by death date
pos_df = covid.scrape_widash_postest()
death_df = covid.scrape_widash_deaths()

# Combine in one DF
pos_lag = pos_df[['Date', 'Positive']]
pos_lag.Date = pos_lag.Date + datetime.timedelta(days=lag)
lagcol = 'Positives +' + str(lag) + ' days'

plotdata = pos_df.set_index('Date')
plotdata[lagcol] = pos_lag.set_index('Date')['Positive']
plotdata['Deaths'] = death_df.set_index('Date')['Total']
plotdata = plotdata.reset_index()


# Make a plot
plotpath = '.\\docs\\_includes\\plotly'
savefile = plotpath+'\\Cases-Deaths-WI.html'

fig = covid.plotly_twolines(
    plotdata, 
    'Deaths',
    lagcol, 
    plotcolors=['firebrick', 'steelblue', 'rosybrown'],
    secondary_scale=1/cfr,
    # date_min=datetime.datetime(2021,1,15),
    range_max=90,
    col1_mode='avg-bar',
    col2_mode='avg',
    plotlabels = {'title': 'Deaths vs Positive tests - WI',
                  'yaxis': 'Deaths',
                  'yaxis_secondary': 'Positive tests',
                  },
    savefile=savefile,
    showfig=False,
    )

fig.update_xaxes(title_text='Date of death')
# fig.update_yaxes(secondary_y=True, tickformat=',.0%')
# fig.update_traces(secondary_y=True, hovertemplate='%{y:.1%}')


fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)


save_png = '.\\docs\\assets\\Cases-Deaths-WI.png'
fig.write_image(
    save_png,
    width=700,
    height=400,
    engine='kaleido',
)
os.startfile(save_png)

#%%
exit


#%%


# add deaths; set index as date temporarily so they merge correctly
cases = cases.set_index('Date')
temp_deaths = covid.read_deathdate_wi(death_filename).set_index('Date')
cases[death_latest] = temp_deaths['Confirm + Probable deaths']

# add reported cases
cases['Cases (reported)'] = state.set_index('Date').Cases
cases['Deaths (reported)'] = state.set_index('Date').Deaths

# # switch to reported
# case_latest = 'Cases (reported)'
# death_latest = 'Deaths (reported)'

# state
lag = 14
cfr = 0.012

# # Milwaukee
# lag = 16
# cfr = 0.01

death2 = cases[death_latest].reset_index(drop=False)
death2['Date'] = death2['Date'] - datetime.timedelta(days=lag)
cases[death_latest] = death2.set_index('Date')[death_latest] / cfr

cases = cases.rolling(7).mean()
cases = cases.reset_index(drop=False)

# cases.plot(x='Date', y=[case_latest, 'Cases (reported)'])

# cases.plot(x='Date', y=[case_latest, death_latest])



fig = px.line(
    cases, 
    x='Date',
    y=[case_latest, death_latest], 
    color_discrete_sequence=['steelblue', 'firebrick'],
    title='Cases by test date vs Deaths by death date<br>'
          +'(7-day avg, 14-day lag, CFR 1.2%)',
    labels={'value': 'Cases / day'}
    )
fig.update_layout(legend_title='')

pngfile = 'docs\\assets\\Cases-Deaths-Match_2021-04-15.png'
fig.write_image(
    pngfile,
    width=700,
    height=500,
    engine='kaleido',
    )
os.startfile(pngfile)






