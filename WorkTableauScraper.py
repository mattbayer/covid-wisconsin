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

#%% vaccine allocation

url = 'https://bi.wisconsin.gov/t/DHS/views/VaccineDistribution/Allocated?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'


ts = TS()
ts.loads(url)
allocation_dash = ts.getWorkbook()

for t in allocation_dash.worksheets:
    #show worksheet name
    print(f"WORKSHEET NAME : {t.name}")
    #show dataframe for this worksheet
    print(t.data)
    
    
# Vaccine by county and age
url = 'https://bi.wisconsin.gov/t/DHS/views/VaccinesAdministeredtoWIResidents_16129838459350/VaccinatedWisconsin-County?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
ts.loads(url)
vax_dash = ts.getWorkbook()

for t in vax_dash.worksheets:
    #show worksheet name
    print(f"WORKSHEET NAME : {t.name}")
    #show dataframe for this worksheet
    print(t.data)

datafile = 'data\\vaccinations\\vax-dashboards_2021-04-27.pkl'
with open(datafile, 'wb') as f:
    pickle.dump([allocation_dash, vax_dash], f)
    
    
#%% load vaccine dash and process

datafile = 'data\\vaccinations\\vax-dashboards_2021-04-26.pkl'
with open(datafile, 'rb') as f:
    allocation_dash, vax_dash = pickle.load(f)
    
#%% data cleaning
    
admin = allocation_dash.worksheets[0].data
col_rename = {'SUM(Immunization Count)-value': 'Immunizations', 
              'SUM(Immunization Count)-alias': 'Immunizations 7-day',
              'DAY(Vaccination Date)-value': 'Date'
              }
admin = admin[col_rename.keys()]
admin = admin.rename(columns=col_rename)
admin.Date = pd.to_datetime(admin.Date.copy())
admin['Immunizations 7-day'] = pd.to_numeric(admin['Immunizations 7-day'].apply(lambda s: s.replace(',', '')))
    
#%% manufacturer counts
manufacturer = allocation_dash.worksheets[1].data
col_rename = {'Trade Name-value': 'Trade Name',
              'SUM(Immunization Count)-alias': 'Count'}
manufacturer = manufacturer[col_rename.keys()]
manufacturer = manufacturer.rename(columns=col_rename)
manufacturer.Count = pd.to_numeric(manufacturer.Count.copy())
manufacturer = manufacturer.set_index('Trade Name').T

# Will not necessarily match the sum of all the trade names
manufacturer['All'] = allocation_dash.worksheets[2].data.iloc[0,1]
manufacturer['Reporting date'] = pd.to_datetime(allocation_dash.worksheets[2].data.iloc[0,2])

# Rename stuff
manufacturer = manufacturer.reset_index(drop=True)
manufacturer.columns.name = ''

    
#%% Get positives/tests

pos_url = 'https://bi.wisconsin.gov/t/DHS/views/PercentPositivebyTestPersonandaComparisonandTestCapacity/PercentPositivebyTestDashboard?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'

ts.loads(pos_url)
pos_dash = ts.getWorkbook()
pos_sheet = pos_dash.worksheets[0]



#%% 

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