# -*- coding: utf-8 -*-
"""
Create plots showing vaccine effectiveness over time

Created on Tue Dec 14 22:20:54 2021

@author: matt_
"""

import pandas as pd
import datetime
from plotly.offline import plot as pplot
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
import covid

from tableauscraper import TableauScraper as TS
ts = TS()  

#%% Load the age-adjusted table from DHS

datasets = ['Cases', 'Hospitalizations', 'Deaths']

urls = {'Cases': 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus_16303581926310/CasesbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link',
        'Hospitalizations': 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus_16303581926310/HospitalizationsbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link',
        'Deaths': 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus_16303581926310/DeathsbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link',
        }

#%%

for outcome in datasets:
    ts.loads(urls[outcome])
    dashboard = ts.getWorkbook()
    data = dashboard.getWorksheet(outcome).data
    data = data.iloc[:, [0,3,4]]
    col_rename = {'Month*-value': 'Month', 'Measure Names-alias': 'Measure', 'Measure Values-alias': 'Value'}
    data = data.rename(columns=col_rename)
    data = data.pivot(index='Month', columns='Measure', values='Value')
    col_rename = {'Age-adjusted rate of ' + outcome.lower() + ' per 100,000 fully vaccinated people': 'Vax',
                  'Age-adjusted rate of ' + outcome.lower() + ' per 100,000 not fully vaccinated people': 'Unvax',
                  'Percent of people who completed the vaccine series by the middle of the month': 'Fully Vax %'
                  }
    data = data.rename(columns=col_rename)
    data = data.drop('Fully Vax %', axis=1)
    data.columns.name = outcome + ' per 100k'
    print(data)
    

#%% Load all the saved data

months = list(range(8,12))  # months 8:11 inclusive

for m in months:
    filestr = 'Breakthroughs_2021-' + str(m).zfill(2) + '.csv'
    print(filestr)