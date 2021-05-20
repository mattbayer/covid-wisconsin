# -*- coding: utf-8 -*-
"""
Estimate the total number of people immune.

Created on Thu May 20 12:58:30 2021

@author: 212367548
"""

import covid

import pandas as pd
import plotly.express as px
import os

from tableauscraper import TableauScraper as TS


#%% Helper functions
def loads_with_retries(ts, url, retries):
    for attempt in range(retries):
        try:
            ts.loads(url)
        except Exception as e:
            err = e
            print('Retrying TS load...')
        else:
            break
    else:
        raise err    
    return ts

#%% Get cases by age group
# Pull from tableau instead of downloadable data, because the tableau plot has
# the right age groups to match up with vaccinations.

url = 'https://bi.wisconsin.gov/t/DHS/views/Agegroupovertime/Cases?:embed_code_version=3&:embed=y&:loadOrderID=3&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'

ts = TS()       
ts = loads_with_retries(ts, url, 3)

age_dash = ts.getWorkbook()

age_total = age_dash.worksheets[0].data

col_rename = {'New Age Groups-alias': 'Age group',
              'CNTD(Incident ID)-alias': 'Cases',
              'SUM(case rate by age for 100K )-alias': 'Cases per 100K',
              'WEEK(Episode Date Trunc)-value': 'Week of'}

age_total = age_total[col_rename.keys()]
age_total = age_total.rename(columns=col_rename)
age_total['Week of'] = pd.to_datetime(age_total['Week of'])

# only need the most recent cumulative number
age_total = age_total[age_total['Week of'] == age_total['Week of'].max()]

# set age group to index
age_total = age_total.set_index('Age group')


#%% Get vax by age group from WI DHS data

vax_age_file = 'data\\vaccinations\\Vax-Age-WI.csv'
vax_age = pd.read_csv(vax_age_file, converters={'Reporting date': pd.to_datetime})

# trim to most recent numbers
vax_age = vax_age[vax_age['Reporting date'] == vax_age['Reporting date'].max()]
vax_age = vax_age.drop('Reporting date', axis=1)

# set age group to index
vax_age = vax_age.set_index('Age group')


#%% Do estimates
# Note that populations for vax and cases differ by up to ~3.5%
inf_factor = 3

age_total['Population'] = age_total['Cases'] / age_total['Cases per 100K'] * 1e5

age_total['Est Infected %'] = age_total['Cases per 100K'] / 1000 * inf_factor

# create <18 index for vax_age
vax_age['Population'] = vax_age['Initiated #'] / vax_age['Initiated %']
# vax_age.loc['<18', 'Initiated #'] = 