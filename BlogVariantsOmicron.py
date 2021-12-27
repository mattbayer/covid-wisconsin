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

#%% create number and fraction dataframes

wi_num = covariants_wi.copy()


col_rename = {'total_sequences': 'Total',
              'Alpha': 'Alpha', 
              'Delta': 'Delta',
              'Omicron': 'Omicron'}

wi_num['Week'] = pd.to_datetime(wi_num.week)

wi_num = wi_num.set_index('Week')
wi_num = wi_num[col_rename.keys()]
wi_num = wi_num.rename(columns=col_rename)

wi_num['Other'] = wi_num['Total'] - wi_num['Alpha'] - wi_num['Delta'] - wi_num['Omicron']

wi_frac =wi_num.div(wi_num['Total'], axis='rows')

# wi['Alpha'] = wi['Alpha #'] / wi['Total']
# wi['Delta'] = wi['Delta #'] / wi['Total']
# wi['Omicron'] = wi['Omicron #'] / wi['Total']

# wi.plot(y=['Alpha (B.1.1.7)', 'Delta (B.1.617.2)', 'Other variants'])

#%% plotly version
plotdata = wi_frac.copy() #wi[['Alpha (B.1.1.7) fraction', 'Delta (B.1.617.2) fraction', 'Other variants']]
plotdata.index.name='Date'
plotdata = plotdata.reset_index()
plotdata = plotdata[plotdata.Date >= pd.to_datetime('2021-01-15')]

fig = px.area(
    plotdata,
    x='Date',
    y=['Omicron', 'Delta', 'Alpha', 'Other'], 
    color_discrete_sequence=['black', 'darkblue', 'tomato', 'gray'],
    labels={'value':'Variant share', 'variable':'Variant'},
    title='Coronavirus variant share in WI')

savefile = '.\\docs\\assets\\plotly\\Variant-Fraction.html'
fig.write_html(
    file=savefile,
    default_height=400,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)


save_png = '.\\docs\\assets\\Variant-Fraction_2021-12-27.png'
fig.write_image(
    save_png,
    width=700,
    height=400,
    engine='kaleido',
)
os.startfile(save_png)


#%% Get case data by test date

start_date = pd.to_datetime('2021-01-15')
end_date = pd.to_datetime('2021-12-27')

plotdata = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))
# plotdata['Cases'] = widata.set_index('Date')['POS_NEW']
# plotdata['Cases 7-day'] = widata.set_index('Date')['POS_NEW'].rolling(7).mean()

pos_df = covid.scrape_widash_postest()

plotdata['Cases'] = pos_df.set_index('Date')['Positive']
plotdata['Cases 7-day'] = plotdata.Cases.rolling(7).mean()

#%% Plot cases by proportion of variants
variants_temp = wi_frac.copy()
# advanced dates one week, so they're plotted in the middle of the sum range
variants_temp.index = variants_temp.index + datetime.timedelta(days=7)

plotdata['Alpha fraction'] = variants_temp['Alpha']
plotdata['Delta fraction'] = variants_temp['Delta']
plotdata['Omicron fraction'] = variants_temp['Omicron']
plotdata['Other fraction'] = variants_temp['Other']
plotdata[['Alpha fraction', 'Delta fraction', 'Omicron fraction', 'Other fraction']] = plotdata[['Alpha fraction', 'Delta fraction', 'Omicron fraction', 'Other fraction']].interpolate()

plotdata['Alpha'] = plotdata['Alpha fraction'] * plotdata['Cases 7-day']
plotdata['Delta'] = plotdata['Delta fraction'] * plotdata['Cases 7-day']
plotdata['Omicron'] = plotdata['Omicron fraction'] * plotdata['Cases 7-day']
plotdata['Other variants'] = plotdata['Other fraction'] * plotdata['Cases 7-day']

plotdata.index.name = 'Date'
plotdata = plotdata[~np.isnan(plotdata['Other variants'])]

fig = px.area(
    plotdata.reset_index(),
    x='Date',
    y=['Omicron', 'Delta', 'Alpha', 'Other variants'], 
    # color_discrete_sequence=['darkgreen', 'rgb(209, 52, 52)', 'gray'],
    color_discrete_sequence=['black', 'darkblue', 'tomato', 'gray'],
    labels={'value':'Cases/day', 'variable':'Variant'},
    title='Estimated cases by variant in WI')

savefile = '.\\docs\\assets\\plotly\\Variant-Cases.html'
fig.write_html(
    file=savefile,
    default_height=400,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)



save_png = '.\\docs\\assets\\Variant-Cases_2021-12-27.png'
fig.write_image(
    save_png,
    width=700,
    height=400,
    engine='kaleido',
)
os.startfile(save_png)


