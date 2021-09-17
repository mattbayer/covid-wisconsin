# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 13:14:28 2021

@author: 212367548
"""

import pandas as pd
import datetime
from plotly.offline import plot as pplot
import plotly.express as px
import plotly.graph_objects as go
import os

import covid

from tableauscraper import TableauScraper as TS
ts = TS()  

#%% process monthly data

case_url = 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus/CasesbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
hosp_url = 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus/HospitalizationsbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
death_url = 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus/DeathsbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=2&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'

ts.loads(case_url)
case_dash = ts.getWorkbook()

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


#%% process age tables

age_case_url = 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatusAge/Cases?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
age_hosp_url = 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatusAge/Hospitalizations?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
age_death_url = 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatusAge/Deaths?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'


ts.loads(age_case_url)
case_dash = ts.getWorkbook()


#%% variable width graph
# based loosely on mekko example from plotly documentation https://plotly.com/python/bar-charts/
import numpy as np

pop_age = covid.read_pop_age_wi()

# get age group labels from pop_age
labels = list(pop_age.index)
labels.remove('All')

widths = {'Vax': np.array([10,20,30,40]),
          'Unvax': np.array([50,30,20,10])}

widths_total = widths['Vax'] + widths['Unvax']

data = {
    "Vax": [1,2,3,4],
    "Unvax": [10,20,30,40]
}

fig = go.Figure()
for key in data:
    x = np.cumsum(widths_total) - widths['Unvax']
    if key == 'Vax':
        x = x - widths['Vax']
        
    fig.add_trace(go.Bar(
        name=key,
        y=data[key],
        x=x,
        width=widths[key],
        offset=0,
        customdata=np.transpose([labels, widths[key]*data[key]]),
        texttemplate="%{y} x %{width} =<br>%{customdata[1]}",
        textposition="inside",
        textangle=0,
        textfont_color="white",
        hovertemplate="<br>".join([
            "label: %{customdata[0]}",
            "width: %{width}",
            "height: %{y}",
            "area: %{customdata[1]}",
        ])
    ))

fig.update_xaxes(
    tickvals=np.cumsum(widths_total)-widths_total/2,
    ticktext= ["%s<br>%d" % (l, w) for l, w in zip(labels, widths_total)]
)

# fig.update_xaxes(range=[0,100])
# fig.update_yaxes(range=[0,100])

fig.update_layout(
    title_text="Cases by Age and Vax - Testing",
    uniformtext=dict(mode="hide", minsize=10),
)

savefile = '.\\docs\\assets\\plotly\\VaxBarAge.html'
fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)