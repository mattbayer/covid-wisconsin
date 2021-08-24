# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 13:14:28 2021

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

case_url = 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus/CasesbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
hosp_url = 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus/HospitalizationsbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
death_url = 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus/DeathsbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=2&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'


ts.loads(case_url)
case_dash = ts.getWorkbook()

#%% 
cases = case_dash.getWorksheet('Cases').data
col_rename = {'Month*-value': 'Month',
              'Measure Names-alias': 'Measure',
              'Measure Values-alias': 'value'}
cases = cases[col_rename.keys()]
cases = cases.rename(columns=col_rename)

# convert every value to numeric, some of which are percents
cases['value'] = pd.to_numeric(cases['value'].apply(lambda v: v.replace('%', '')))

# pivot to column format
cases = cases.pivot(index='Month', columns='Measure', values='value')
cases = cases.rename(columns=
                     {'Confirmed and probable COVID-19 case rate per 100,000 not fully vaccinated people': 'Non-vax rate',
                      'Confirmed and probable COVID-19 case rate per 100,000 fully vaccinated people': 'Vax rate',
                      'Percent of people who completed the vaccine series by the first of the month': 'Percent vax'
                      })

# replace index with month number for sorting
cases = cases.reset_index()
cases['Month number'] = cases.Month.apply(lambda m: datetime.datetime.strptime(m, '%B').month)
cases = cases.set_index('Month number', drop=True)
cases = cases.sort_index()

# Create efficacy and relative risk columns
cases['Relative risk'] = cases['Vax rate'] / cases['Non-vax rate']
cases['Efficacy'] = 1 - cases['Relative risk']


#%% adjust for previously infected?
pop_wi = 5.9e6

vax_rate = cases.loc[7, 'Vax rate']
vax_perc = cases.loc[7, 'Percent vax']
vax_pop = vax_perc/100 * pop_wi
vax_num = vax_rate/1e5 * vax_pop

non_rate = cases.loc[7, 'Non-vax rate']
non_perc = 100 - vax_perc
non_pop = non_perc/100 * pop_wi
non_num = non_rate/1e5 * non_pop

pre_frac = 0.3
nonpre_pop = non_perc/100 * pre_frac * pop_wi
nonpre_num = vax_rate/1e5 * nonpre_pop

non2_num = non_num - nonpre_num
non2_pop = non_pop - nonpre_pop
non2_rate = non2_num / non2_pop * 1e5
