# -*- coding: utf-8 -*-
"""
Blog work on variants.

Created on Mon Feb 15 10:19:50 2021
Updated for Delta beginning Jun 30 2021

@author: 212367548
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import covid
import urllib
from scipy import signal
import datetime
import os


#%% Get the data

# # covid data
# widata = covid.read_covid_data_wi('state')

start_date = pd.to_datetime('2021-03-01')
end_date = pd.to_datetime('2021-08-06')

plotdata = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))
# plotdata['Cases'] = widata.set_index('Date')['POS_NEW']
# plotdata['Cases 7-day'] = widata.set_index('Date')['POS_NEW'].rolling(7).mean()



#%% Get data by test date

pos_df = covid.scrape_widash_postest()

plotdata['Cases'] = pos_df.set_index('Date')['Positive']
plotdata['Cases 7-day'] = plotdata.Cases.rolling(7).mean()

#%% Alternative data sources to GISAID

# covariants.org
# nice because they compile the GISAID data into a file on github
# disadvantage is that it's already aggregated to 2-week blocks
covariants = pd.read_json('https://raw.githubusercontent.com/hodcroftlab/covariants/master/cluster_tables/USAClusters_data.json')
covariants_wi = pd.DataFrame(covariants.loc['Wisconsin', 'countries'])
covariants_wi.plot(x='week', y=['total_sequences', '20I (Alpha, V1)', '21A (Delta)'])

# I believe week is "two-week period beginning..."

#%%
wi = covariants_wi.copy()
col_rename = {'total_sequences': 'Total',
              '20I (Alpha, V1)': 'Alpha', 
              '21A (Delta)': 'Delta'}

wi['Week'] = pd.to_datetime(wi.week)
wi = wi.set_index('Week')
wi = wi[col_rename.keys()]
wi = wi.rename(columns=col_rename)
wi['Alpha (B.1.1.7) fraction'] = wi['Alpha'] / wi['Total']
wi['Delta (B.1.617.2) fraction'] = wi['Delta'] / wi['Total']
wi['Other strains'] = 1 - wi['Alpha (B.1.1.7) fraction'] - wi['Delta (B.1.617.2) fraction']

wi.plot(y=['Alpha (B.1.1.7) fraction', 'Delta (B.1.617.2) fraction', 'Other strains'])



#%% Estimates

# model_start = pd.to_datetime('2021-05-09')
# DeltaR = 1.5   # factor that Delta's R exceeds the current mix of strains
# R1 = 0.75
# start = 560

model_start = pd.to_datetime('2021-05-17')
DeltaR = 1.77   # factor that Delta's R exceeds the current mix of strains
R1 = 0.7
start = 430

N = (end_date - model_start).days + 1

R2 = R1*DeltaR
s = 5   # serial interval, 5 days
d = np.arange(0,N)

 # 4% at May 24 from covariants data, apply the R factor and time delay to start date
delay = (model_start - pd.to_datetime('2021-05-24')).days
frac2 = 0.04 * DeltaR**(delay/s)   

v1 = start * np.exp((R1-1)*d/s)
v2 = frac2 * start * np.exp((R2-1)*d/s)


plotdata.loc[model_start:,'Prior trend'] = v1
plotdata.loc[model_start:,'Delta trend'] = v2
plotdata.loc[model_start:,'Model total'] = v1 + v2

plotdata.index.name = 'Date'


#%% Load gisaid estimates

gisaid_all = pd.read_csv('data\\sequences\\gisaid-all-WI.csv')
gisaid_b117 = pd.read_csv('data\\sequences\\gisaid-b117-WI.csv')

variants = gisaid_all.groupby('Collection date').count()
variants['All'] = variants['Accession ID']
variants = variants.drop(['Virus name', 'Accession ID'], axis=1)
variants['B117'] = gisaid_b117.groupby('Collection date').count()['Accession ID']
variants = variants.fillna(0)

var_smooth = variants.rolling(7).sum()
variants['B117 fraction'] = var_smooth['B117'] / var_smooth['All']

variants.index.name = 'Date'
variants.index = pd.to_datetime(variants.index)
variants = variants.loc[datetime.datetime(2021,1,1):datetime.datetime(2021,3,27)]

plotdata['B117 estimate'] = plotdata['Cases 7-day'] * variants['B117 fraction']

#%% Use covariants estimates

plotdata2 = wi
# advanced dates one week, so they're plotted in the middle of the sum range
plotdata2.index = plotdata2.index + datetime.timedelta(days=7)
# limit dates
plotdata2 = plotdata2.loc[(plotdata2.index >= start_date) & (plotdata2.index <= end_date)].copy()
plotdata2['Delta estimate'] = plotdata['Cases 7-day'] * plotdata2['Delta fraction']
plotdata2['Alpha estimate'] = plotdata['Cases 7-day'] * plotdata2['Alpha fraction']


#%% Plot

# fig = px.line(plotdata, y=['Cases 7-day', 'Classic', 'B.1.1.7', 'Model total'])
fig = px.area(
    plotdata, 
    y=['Delta trend', 'Prior trend'], 
    color_discrete_sequence=['tomato', 'lightsteelblue'],
    title='<i><b>Possible</i></b> Delta variant trend in WI',
    labels={'index':'Date', 'value': 'Cases / day'}
    )

fig.add_trace(
    go.Scatter(
        x=plotdata.index,
        y=plotdata['Cases 7-day'],
        name='Cases (7-day avg)',
        marker_color='steelblue',
        )
    )

fig.add_trace(
    go.Scatter(
        x=plotdata2.index,
        y=plotdata2['Alpha estimate'],
        name='Alpha estimate',
        marker_color='saddlebrown',
        line_dash='dot'
        )
    )

fig.add_trace(
    go.Scatter(
        x=plotdata2.index,
        y=plotdata2['Delta estimate'],
        name='Delta estimate',
        marker_color='darkred',
        line_dash='dot'
        )
    )




fig.update_layout(legend_traceorder='reversed', legend_title='')

            # fig.add_trace(
            #     go.Bar(
            #         x=data1.index, 
            #         y=data1.iloc[:,gg],
            #         name=data1_label, 
            #         marker_color=plotcolors[2], 
            #         hovertemplate='%{y:.0f}',
            #         showlegend=showlegend,
            #         ),
            #     row=sub_row[gg],
            #     col=sub_col[gg],
            #     )
        
# save as html, with plotly JS library loaded from CDN
htmlfile='docs\\assets\\plotly\\Variant-Estimate.html'
fig.write_html(
    file=htmlfile,
    default_height=500,
    include_plotlyjs='cdn',
    )      

pngfile = 'docs\\assets\\Variant-Estimate.png'
fig.write_image(
    pngfile,
    width=700,
    height=500,
    engine='kaleido',
    )

os.startfile(htmlfile)
os.startfile(pngfile)
