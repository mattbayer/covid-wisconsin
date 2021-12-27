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




#%% Alternative data sources to GISAID

# covariants.org
# nice because they compile the GISAID data into a file on github
# disadvantage is that it's already aggregated to 2-week blocks
covariants = pd.read_json('https://raw.githubusercontent.com/hodcroftlab/covariants/master/cluster_tables/USAClusters_data.json')
covariants_wi = pd.DataFrame(covariants.loc['Wisconsin', 'countries'])

# Select and consolidate strains of interest
variants = ['Alpha', 'Delta', 'Omicron']
# sometimes variants have multiple strains, so sum these together
for var in variants:
    all_strains = [s for s in covariants_wi.columns if var in s]
    covariants_wi[var] = covariants_wi[all_strains].sum(axis=1)

# preliminary plot
covariants_wi.plot(x='week', y=['total_sequences'] + variants)

# I believe week is "two-week period beginning..."

#%%
wi = covariants_wi.copy()
col_rename = {'total_sequences': 'Total',
              '20I (Alpha, V1)': 'Alpha', 
              'All Delta': 'Delta'}

wi['Week'] = pd.to_datetime(wi.week)
wi = wi.set_index('Week')
wi = wi[col_rename.keys()]
wi = wi.rename(columns=col_rename)
wi['Alpha (B.1.1.7)'] = wi['Alpha'] / wi['Total']
wi['Delta (B.1.617.2)'] = wi['Delta'] / wi['Total']
wi['Other variants'] = 1 - wi['Alpha (B.1.1.7)'] - wi['Delta (B.1.617.2)']

# wi.plot(y=['Alpha (B.1.1.7)', 'Delta (B.1.617.2)', 'Other variants'])

#%% plotly version
plotdata = wi #wi[['Alpha (B.1.1.7) fraction', 'Delta (B.1.617.2) fraction', 'Other variants']]
plotdata.index.name='Date'
plotdata = plotdata.reset_index()
plotdata = plotdata[plotdata.Date >= pd.to_datetime('2021-01-15')]

fig = px.area(
    plotdata,
    x='Date',
    y=['Delta (B.1.617.2)', 'Alpha (B.1.1.7)', 'Other variants'], 
    color_discrete_sequence=['darkblue', 'tomato', 'gray'],
    labels={'value':'Variant share', 'variable':'Variant'},
    title='Coronavirus variant share in WI')

savefile = '.\\docs\\assets\\plotly\\Variant-Fraction.html'
fig.write_html(
    file=savefile,
    default_height=400,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)


save_png = '.\\docs\\assets\\Variant-Fraction.png'
fig.write_image(
    save_png,
    width=700,
    height=400,
    engine='kaleido',
)
os.startfile(save_png)


#%% Get case data by test date

start_date = pd.to_datetime('2021-01-15')
end_date = pd.to_datetime('2021-07-27')

plotdata = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))
# plotdata['Cases'] = widata.set_index('Date')['POS_NEW']
# plotdata['Cases 7-day'] = widata.set_index('Date')['POS_NEW'].rolling(7).mean()

pos_df = covid.scrape_widash_postest()

plotdata['Cases'] = pos_df.set_index('Date')['Positive']
plotdata['Cases 7-day'] = plotdata.Cases.rolling(7).mean()

#%% Plot cases by proportion of variants
variants_temp = wi.copy()
# advanced dates one week, so they're plotted in the middle of the sum range
variants_temp.index = variants_temp.index + datetime.timedelta(days=7)

plotdata['Alpha fraction'] = variants_temp['Alpha (B.1.1.7)']
plotdata['Delta fraction'] = variants_temp['Delta (B.1.617.2)']
plotdata['Other fraction'] = variants_temp['Other variants']
plotdata[['Alpha fraction', 'Delta fraction', 'Other fraction']] = plotdata[['Alpha fraction', 'Delta fraction', 'Other fraction']].interpolate()

plotdata['Alpha (B.1.1.7)'] = plotdata['Alpha fraction'] * plotdata['Cases 7-day']
plotdata['Delta (B.1.617.2)'] = plotdata['Delta fraction'] * plotdata['Cases 7-day']
plotdata['Other variants'] = plotdata['Other fraction'] * plotdata['Cases 7-day']

plotdata.index.name = 'Date'
plotdata = plotdata[~np.isnan(plotdata['Other variants'])]

fig = px.area(
    plotdata.reset_index(),
    x='Date',
    y=['Delta (B.1.617.2)', 'Alpha (B.1.1.7)', 'Other variants'], 
    # color_discrete_sequence=['darkgreen', 'rgb(209, 52, 52)', 'gray'],
    color_discrete_sequence=['darkblue', 'tomato', 'gray'],
    labels={'value':'Cases/day', 'variable':'Variant'},
    title='Estimated cases by variant in WI')

savefile = '.\\docs\\assets\\plotly\\Variant-Cases.html'
fig.write_html(
    file=savefile,
    default_height=400,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)



save_png = '.\\docs\\assets\\Variant-Cases.png'
fig.write_image(
    save_png,
    width=700,
    height=400,
    engine='kaleido',
)
os.startfile(save_png)

#%% Estimates

exit

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



#%% Use covariants estimates

plotdata2 = wi.copy()
# advanced dates one week, so they're plotted in the middle of the sum range
plotdata2.index = plotdata2.index + datetime.timedelta(days=7)
# limit dates
plotdata2 = plotdata2.loc[(plotdata2.index >= start_date) & (plotdata2.index <= end_date)].copy()
plotdata2['Delta estimate'] = plotdata['Cases 7-day'] * plotdata2['Delta (B.1.617.2)']
plotdata2['Alpha estimate'] = plotdata['Cases 7-day'] * plotdata2['Alpha (B.1.1.7)']


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
