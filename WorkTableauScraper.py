# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 09:22:05 2021

@author: 212367548
"""


import pandas as pd
import datetime
from plotly.offline import plot as pplot
import plotly.express as px
import os
import pickle

import covid

from tableauscraper import TableauScraper as TS

#%% Setup and helper function for updating a file

ts = TS()      

def update_file(filename, update, on):
    # load file of previous data
    compiled = pd.read_csv(filename)
        
    # first update any overlapping data
    # set indices to the "on" columns, for both previous and updated data
    compiled = compiled.set_index(on)
    update = update.set_index(on)
    compiled.update(update)
    
    # then reset indices and do a merge to add new data
    compiled = compiled.reset_index()
    update = update.reset_index()
    compiled = pd.merge(compiled, update, how='outer')
        
    # save updated file
    compiled.to_csv(filename, index=False)   




    
#%% how to load previously saved vaccine dash

# datafile = 'data\\vaccinations\\vax-dashboards_2021-05-02.pkl'
# with open(datafile, 'rb') as f:
#     # allocation_dash, vax_dash = pickle.load(f)
#     allocation_dash, vax_dash, vax_complete = pickle.load(f)
    


#%% Extract data for vaccines by county

# # vax_dash.worksheets[0].data.to_csv('data\\temp.csv')

# col_rename = {'Region-value': 'Region',
#               'County-value': 'County',
#               'Measure Names-alias': 'Measure',
#               'Measure Values-alias': 'value'}

# county = vax_dash.worksheets[0].data[col_rename.keys()]
# county = county.rename(columns=col_rename)


    
#%% Get positives/tests

pos_url = 'https://bi.wisconsin.gov/t/DHS/views/PercentPositivebyTestPersonandaComparisonandTestCapacity/PercentPositivebyTestDashboard?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
# https://bi.wisconsin.gov/t/DHS/views/PercentPositivebyTestPersonandaComparisonandTestCapacity/PercentPositivebyTestDashboard?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link
ts.loads(pos_url)
pos_dash = ts.getWorkbook()
pos_sheet = pos_dash.worksheets[0]


# data here not in pos_sheet.data for some reason - that's all zeros - but in selectable items
# Many of the columns are repeated, and appear to contain the same data but 
# reversed in time. The code below only keeps the second of each repeated 
# column, which I think is fine.
data = pos_sheet.getSelectableItems()
pos_dict = dict()
pos_df = pd.DataFrame()
for d in data[1::2]:
    if d['column'] != 'Measure Values':
        # this column is too long and also redundant
        pos_dict[d['column']] = d['values']
        pos_df[d['column']] = d['values']

col_rename = {'SUM(Number of Positives)': 'Positive',
              'SUM(Number of Negatives)': 'Negative',
              'DAY(Encounter Date)': 'Date', 
              'AGG(Percent_Positive_tt)': 'Percent Positive'}

pos_df = pos_df[col_rename.keys()]
pos_df = pos_df.rename(columns=col_rename)

pos_df.Date = pd.to_datetime(pos_df.Date)
pos_df['Tests'] = pos_df['Positive'] + pos_df['Negative']

#%% Plotly plot for cases / positivity
plotpath = '.\\docs\\assets\\plotly'

# covid.plotly_twolines(
#     pos_df, 
#     'Percent Positive', 
#     'Positive', 
#     plotcolors=['violet', 'steelblue', 'thistle'],
#     secondary_scale=300,
#     savefile=plotpath+'\\Pos-Positivity-WI.html',
#     )

covid.plotly_twolines(
    pos_df, 
    'Positive', 
    'Percent Positive', 
    plotcolors=['steelblue', 'violet', 'lightsteelblue'],
    secondary_scale=1/200,
    range_max=8000,
    savefile=plotpath+'\\Pos-Positivity-WI.html',
    )

covid.plotly_twolines(
    pos_df, 
    'Positive', 
    'Tests', 
    plotcolors=['steelblue', 'olivedrab', 'lightsteelblue'],
    secondary_scale=10,
    range_max=8000,
    savefile=plotpath+'\\Pos-Tests-WI.html',
    )

#%% Get county-level cases

ccase_url = 'https://bi.wisconsin.gov/t/DHS/views/County-leveldailycasesconfirmedandprobable_16214282004490/Countydailycases?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
ts.loads(ccase_url)
ccase_dash = ts.getWorkbook()



#%% Get county-level deaths

cdeath_url = 'https://bi.wisconsin.gov/t/DHS/views/County-leveldailydeathsconfirmedandprobable_16214287829690/Countydailydeaths?:embed_code_version=3&:embed=y&:loadOrderID=3&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'

ts.loads(cdeath_url)
cdeath_dash = ts.getWorkbook()

update_date = cdeath_dash.worksheets[0].data.iloc[0,-1]
update_date = update_date.replace('/', '-')

death_data = cdeath_dash.worksheets[1].data
# death_file = 'data\\Deaths by day auto_' + update_date + '.csv'
# death_data.to_csv(death_file)