# -*- coding: utf-8 -*-
"""
Work on new plots for monitoring the situation.

Created on Wed Jun 30 10:48:03 2021

@author: 212367548
"""

import pandas as pd
import datetime
from plotly.offline import plot as pplot
import plotly.express as px
import os

import covid

from tableauscraper import TableauScraper as TS
ts = TS()


#%% Get positives/tests

pos_url = 'https://bi.wisconsin.gov/t/DHS/views/PercentPositivebyTestPersonandaComparisonandTestCapacity/PercentPositivebyTestDashboard?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'

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