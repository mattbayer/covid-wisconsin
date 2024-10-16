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

#%% Deaths / cases plot

case_df = covid.scrape_widash_cases()
death_df = covid.scrape_widash_deaths()
hosp_df = covid.download_hhs_data_wi()

#%% Put all data into one DF

plotdata = case_df[['Date', 'Confirmed']]
plotdata = plotdata.rename(columns={'Confirmed': 'Cases'})
plotdata = plotdata.set_index('Date')
plotdata['Deaths'] = death_df.set_index('Date')['Confirmed']
plotdata['Admissions'] = hosp_df.set_index('Date')['previous_day_admission_adult_covid_confirmed']
plotdata = plotdata.reset_index()

#%% Function to add shading to preliminary area of plot
def shade_preliminary(fig, x0, x1):
    # shading applied to the x range between x0 and x1
    fig.add_shape(
        type="rect",
        xref='x', x0=x0, x1=x1,
        yref='y domain', y0=0, y1=1,
        line_color='rgba(0,0,0,0)',
        fillcolor='rgba(0,0,0,0.2)',
    )
    fig.add_annotation(
        xanchor='right', xref='x', x=x0,
        yanchor='top', yref='y domain', y=1,
        text='Preliminary<br>data',
        font_color='rgb(0.5,0.5,0.5)',
        align='right',
        showarrow=False,
        ) 

#%% Plot Deaths / Cases
# parameters for comparison
lag = 12
cfr = 0.012

# Make a plot
plotpath = '.\\docs\\_includes\\plotly'
savefile = plotpath+'\\Deaths-Cases-WI.html'

fig = covid.plotly_twolines(
    plotdata, 
    'Deaths',
    'Cases', 
    plotcolors=['firebrick', 'steelblue', 'rosybrown'],
    secondary_scale=1/cfr,
    # date_min=datetime.datetime(2021,1,15),
    range_max=90,
    col1_mode='avg-bar',
    col2_mode='avg',
    plotlabels = {'title': 'Deaths vs Cases - WI<br>(CFR '+str(cfr*100)+'%)',
                  'yaxis': 'Deaths',
                  'yaxis_secondary': 'Cases',
                  },
    savefile=savefile,
    showfig=False,
    )

fig.update_xaxes(title_text='Date of death / Date of test')
# set background with same color as default, but with lower opacity to make it lighter
fig.update_layout(plot_bgcolor='rgba(229, 236, 246, 0.7)')



# shade the recent data using custom function
shade_days = 14
end_date = plotdata.Date.max()
start_date = end_date - datetime.timedelta(days=shade_days) 

shade_preliminary(fig, start_date, end_date)



fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)



#%% Hospitalization plot

# Make a plot
plotpath = '.\\docs\\_includes\\plotly'
savefile = plotpath+'\\Hosp-Cases-WI.html'

hrate = 0.09

fig = covid.plotly_twolines(
    plotdata, 
    'Admissions',
    'Cases', 
    plotcolors=['darkorange', 'steelblue', 'burlywood'],
    secondary_scale=1/hrate,
    # date_min=datetime.datetime(2021,1,15),
    range_max=600,
    col1_mode='avg-bar',
    col2_mode='avg',
    plotlabels = {'title': 'Hospital Admissions vs Cases - WI',
                  'yaxis': 'Admissions',
                  'yaxis_secondary': 'Cases',
                  },
    savefile=savefile,
    showfig=False,
    )

fig.update_xaxes(title_text='Date of admission / Date of test')
# set background with same color as default, but with lower opacity to make it lighter
fig.update_layout(plot_bgcolor='rgba(229, 236, 246, 0.7)')


# shade the recent data using custom function
shade_days = 14
end_date = plotdata.Date.max()
start_date = end_date - datetime.timedelta(days=shade_days) 

shade_preliminary(fig, start_date, end_date)


fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)


#%% 
exit

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








