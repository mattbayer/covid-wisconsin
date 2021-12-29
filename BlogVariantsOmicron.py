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



#%% TSV data from GISAID
# this didn't contain lineage information...

# path = 'data\\sequences'
# tsv_file = 'gisaid_wisconsin_dec_2021-12-27.metadata.tsv'

# gisaid = pd.read_csv(os.path.join(path, tsv_file), sep='\t')


#%% Also tried fasta
# but found out again that these files don't contain lineage information either.
# Previously I was downloading multiple files, filtered by lineage before downloading.

#%% Manual data from WI dashboard

# read csv of manual-input data
manual = pd.read_csv('data/sequences/manual-wi-dashboard.csv')


manual['Total'] = manual.drop('Week', axis=1).sum(axis=1)
manual['Start Date'] = manual.Week.apply(lambda w: datetime.datetime.strptime('2021-'+str(w)+'-1', '%Y-%U-%w'))

# midpoint date for plotting
manual['Date'] = manual['Start Date'] + datetime.timedelta(days=3)

# create fraction dataframe
manual_frac = manual[['Date', 'Delta', 'Omicron', 'Other', 'Total']]
manual_frac = manual_frac.set_index('Date')
manual_frac = manual_frac.div(manual_frac['Total'], axis='rows')


#%% Covariants.org data
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

# change to midweek
wi_num['Date'] = pd.to_datetime(wi_num.week) + datetime.timedelta(days=7)

wi_num = wi_num.set_index('Date')
wi_num = wi_num[col_rename.keys()]
wi_num = wi_num.rename(columns=col_rename)

wi_num['Other'] = wi_num['Total'] - wi_num['Alpha'] - wi_num['Delta'] - wi_num['Omicron']

wi_frac = wi_num.div(wi_num['Total'], axis='rows')

# wi['Alpha'] = wi['Alpha #'] / wi['Total']
# wi['Delta'] = wi['Delta #'] / wi['Total']
# wi['Omicron'] = wi['Omicron #'] / wi['Total']

# wi.plot(y=['Alpha (B.1.1.7)', 'Delta (B.1.617.2)', 'Other variants'])

#%% Combine auto and manual fraction dataframes

wi_frac = wi_frac[wi_frac.index < manual_frac.index.min()]
wi_frac = wi_frac.append(manual_frac)

#%% plotly fraction plot version
end_date_str = '2021-12-29'

start_date = pd.to_datetime('2021-02-15')
end_date = pd.to_datetime(end_date_str)


plotdata = wi_frac.copy() 
plotdata = plotdata.reset_index()
plotdata = plotdata[plotdata.Date >= start_date]

fig = px.area(
    plotdata,
    x='Date',
    y=['Omicron', 'Delta', 'Alpha', 'Other'], 
    color_discrete_sequence=['black', 'darkslateblue', 'tomato', 'gray'],
    labels={'value':'Variant share', 'variable':'Variant'},
    title='Coronavirus variant share in WI')

savefile = '.\\docs\\assets\\plotly\\Variant-Fraction.html'
fig.write_html(
    file=savefile,
    default_height=400,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)


save_png = '.\\docs\\assets\\Variant-Fraction_'+end_date_str+'.png'
fig.write_image(
    save_png,
    width=700,
    height=400,
    engine='kaleido',
)
os.startfile(save_png)


#%% Get case data by test date


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
    # color_discrete_sequence=['black', 'darkblue', 'tomato', 'gray'],
    color_discrete_sequence=['black', 'darkslateblue', 'tomato', 'gray'],
    labels={'value':'Cases/day', 'variable':'Variant'},
    title='Estimated cases by variant in WI')

savefile = '.\\docs\\assets\\plotly\\Variant-Cases.html'
fig.write_html(
    file=savefile,
    default_height=400,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)



save_png = '.\\docs\\assets\\Variant-Cases_'+end_date_str+'.png'
fig.write_image(
    save_png,
    width=700,
    height=400,
    engine='kaleido',
)
os.startfile(save_png)



#%%
exit

#%% extra


#%% Nextstrain metadata download
update = True

if update:
    
    import zipfile
    import requests
    
    zip_url = 'https://data.nextstrain.org/files/ncov/open/metadata.tsv.gz'
    sequences_dir = '.\\data\\sequences\\'
    
    # download the zip file
    r = requests.get(zip_url)
    # write the zip file
    zip_filename = os.path.join(sequences_dir, 'nextstrain_metadata.tsv.gz')
    open(zip_filename, 'wb').write(r.content)
    
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extract('metadata.tsv', path=sequences_dir)
        
    # remove temp zip file
    os.remove(zip_filename)
    
gisaid = pd.read_csv(os.path.join(sequences_dir, 'metadata.tsv'), sep='\t')

#%% Metadata filtering
usa = gisaid[gisaid.country=='USA']
wi = usa[usa.division == 'Wisconsin']
wi.date = pd.to_datetime(wi.date.copy())

def count_by_week(gisaid_data):       
    gisaid_work = gisaid_data.copy()
    gisaid_work['Week of'] = gisaid_work['date'].apply(lambda d: d - datetime.timedelta(days=d.weekday()))
    
    # count the sequences, only keep the count of the sequence name column
    seq_count = gisaid_work.groupby(['Week of', 'Nextstrain_clade']).count().strain
    
    seq_count = seq_count.reset_index(drop=False)
    seq_count = seq_count.rename(columns={'strain': 'count', 'Nextstrain_clade': 'clade'})
    seq_count = seq_count.pivot(index='Week of', columns='clade', values='count')
    
    return seq_count

wi_count = count_by_week(wi)