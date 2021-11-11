# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 10:28:40 2021

@author: 212367548
"""

import covid

import pandas as pd
import numpy as np
import plotly.express as px
import os
from tableauscraper import TableauScraper as TS

#%% Scrape cases by age data

age_cases = covid.scrape_widash_agecases()

#%%
ts = TS()
# scrape the specific kids dashboard
kids_url = 'https://bi.wisconsin.gov/t/DHS/views/Youthagegroupovertime_16219547088360/School-basedages?:embed_code_version=3&:embed=y&:loadOrderID=2&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
ts.loads(kids_url)
kids_dash = ts.getWorkbook()
kids_cases = kids_dash.getWorksheet('Weekly Cases').data

# Select the relevant data and rename
col_rename = {'WEEK(Episode Date Trunc)-value': 'Week of',
              'School entry groups-alias': 'Age group',
              'CNTD(Incident ID)-alias': 'Cases',
              'SUM(case rate by school entry age for 100K)-alias': 'Case rate',
              }
kids_cases = kids_cases[col_rename.keys()]
kids_cases = kids_cases.rename(columns=col_rename)
kids_cases['Week of'] = pd.to_datetime(kids_cases['Week of'])
kids_cases['Cases'] = pd.to_numeric(kids_cases['Cases'])
kids_cases['Case rate'] = pd.to_numeric(kids_cases['Case rate'])

#%% Get population estimate to show the error in the data
kids_cases['Population'] = 100000*kids_cases.Cases / kids_cases['Case rate']
kids_cases[kids_cases['Week of'] == kids_cases['Week of'].max()]

# compare sum across age groups, matches the age_cases <18 number pretty closely
print(kids_cases.groupby('Week of').sum())
print(age_cases[age_cases['Age group']=='<18'])

#%% Plot

date_min = pd.to_datetime('2020-08-01')
date_max = pd.to_datetime('2021-10-31')

range_dates = [date_min, date_max]

range_max = 1100
range_y = np.array([-range_max * 0.05, 1.05*range_max])



htmlfile='docs\\assets\\plotly\\CaseRate-Age.html'
save_png = '.\\docs\\assets\\CaseRate-Age.png'

# line colors copied directly from DHS's plot
colorset = {'<18': 'rgb(78,121,167)',
            '18-24': 'rgb(242,142,43)',
            '25-34': 'rgb(225,87,89)',
            '35-44': 'rgb(118,183,178)',
            '45-54': 'rgb(89,161,79)',
            '55-64': 'rgb(237,201,72)',
            '65+': 'rgb(176,122,161)'}


 
fig = px.line(
    age_cases, 
    x='Week of',
    y='Case rate',
    color='Age group',
    color_discrete_map=colorset,
    title='Case rate per population by age group',
    labels={'value': 'Cases per 100K'}
    )

fig.update_traces(line_width=2.5)
# update axes for date range
fig.update_xaxes({'range': range_dates})
fig.update_yaxes({'range': range_y})

# save as html, with plotly JS library loaded from CDN
fig.write_html(
    file=htmlfile,
    default_height=500,
    default_width=700,
    include_plotlyjs='cdn',
    )   

fig.write_image(
    file=save_png,
    height=450,
    width=700,
    engine='kaleido',
    )   


os.startfile(save_png)

#%%
exit

#%% Cases by age data

cases_age_file = 'data\\Cases-by-age-weekly_2021-04-16.csv'
cases_age = pd.read_csv(cases_age_file)
cases_age.columns = cases_age.loc[0,:]
cases_age = cases_age.loc[1:,:]
as_of = cases_age.loc[1, 'Day of DATE']
cases_age = cases_age.drop(['Day of DATE', 'Measure toggle for title'], axis=1)
cases_age = cases_age.rename(
    columns = {np.nan:'Count/Rate',
               'New Age Groups': 'Age group',
               })
cases_age = cases_age[cases_age['Count/Rate'] != 'Measure toggle']
cases_age = cases_age.melt(id_vars=['Age group', 'Count/Rate'])
cases_age = cases_age.rename(columns = {0: 'Week of'})
cases_age.loc[cases_age['Count/Rate']=='Distinct count of Incident ID', 'Count/Rate'] = 'Count'
cases_age.loc[cases_age['Count/Rate']=='case rate by age for 100K ', 'Count/Rate'] = 'Rate'

cases_age.value = pd.to_numeric(cases_age.value.str.replace(',',''))

count_age = cases_age[cases_age['Count/Rate']=='Count'].drop('Count/Rate', axis=1)
count_age = count_age.pivot(index='Week of', columns='Age group', values = 'value').loc[count_age['Week of'].drop_duplicates(),:]

rate_age = cases_age[cases_age['Count/Rate']=='Rate'].drop('Count/Rate', axis=1)
rate_age = rate_age.pivot(index='Week of', columns='Age group', values = 'value').loc[rate_age['Week of'].drop_duplicates(),:]

share_age = count_age.divide(count_age.sum(axis=1), axis=0)

pop_age = count_age.divide(rate_age, axis=0).mean() * 100e3
sum_list = ['25-34', '35-44', '45-54', '55-64']
# sum_list = ['25-34', '35-44', '45-54']
relative_rate_sum = count_age[sum_list].sum(axis=1)
relative_rate_avg = relative_rate_sum / pop_age[sum_list].sum() * 100e3
relative_rate = rate_age.divide(relative_rate_avg, axis=0)

perc_age = count_age.copy()
# for col in perc_age.columns:
#     perc_age[col] = pd.to_numeric(perc_age[col].str.replace(',',''))


# divide by peak
perc_age = perc_age / perc_age.max()

# divide by certain date
# 65+ first eligible the week of 24-Jan, so start measuring at end of January?
# perc_age = perc_age / perc_age.loc['24-Jan',:]

# divide by average over first 4 weeks of January
# jan = perc_age.loc[['3-Jan','10-Jan','17-Jan','24-Jan'],:]
# perc_age = perc_age / jan.mean()


#%% Plot

colorset = {'<18': 'deepskyblue',
            '18-24': 'green',
            '25-34': 'firebrick',
            '35-44': 'mediumorchid',
            '45-54': 'orangered',
            '55-64': 'darkslategrey',
            '65+': 'gold'}

# get correct order
perc_age = perc_age[colorset.keys()]
share_age = share_age[colorset.keys()]
count_age = count_age[colorset.keys()]
rate_age = rate_age[colorset.keys()]
relative_rate = relative_rate[colorset.keys()]
# limit dates, melt to long format
# plotdata = perc_age.loc['10-Jan':'7-Mar',:].melt(ignore_index=False).reset_index()
plotdata = perc_age.melt(ignore_index=False).reset_index()


# plot_type = 'relative'
plot_type = 'absolute'

if plot_type == 'relative':

    plotdata = relative_rate.loc['4-Oct':'4-Apr',:].melt(ignore_index=False).reset_index()
    htmlfile='docs\\assets\\plotly\\CaseRateRelative-Age-Vaccine.html'
    save_png = '.\\docs\\assets\\CaseRateRelative-Age-Vaccine.png'
    
    fig = px.line(
        plotdata, 
        x='Week of',
        y='value',
        color='Age group',
        color_discrete_map=colorset,
        title='Case rate per population by age group<br>(relative to average rate for ages 25-64)',
        labels={'value': 'Relative case rate'}
        )
    
else:

    plotdata = rate_age.loc['10-Jan':'4-Apr',:].melt(ignore_index=False).reset_index()
    htmlfile='docs\\assets\\plotly\\CaseRate-Age.html'
    save_png = '.\\docs\\assets\\CaseRate-Age.png'
     
    fig = px.line(
        plotdata, 
        x='Week of',
        y='value',
        color='Age group',
        color_discrete_map=colorset,
        title='Case rate per population by age group',
        labels={'value': 'Cases per 100K'}
        )


fig.update_traces(line_width=4,
                  selector=dict(line_color='gold'))

# fig.update_layout(yaxis=dict(tickformat=".0%"))


# add markers
fig.add_annotation(x='24-Jan', y=0, xanchor='left', align='left', showarrow=False,
                   text='65+ vaccine eligible')
fig.update_layout(shapes=[
    dict(
      type= 'line', line_color='gray', line_dash='dash',
      yref= 'paper', y0= 0, y1= 1,
      xref= 'x', x0='24-Jan', x1='24-Jan',
    ),
    ]
)

if plot_type == 'relative':
    fig.add_annotation(x='1-Nov', y=0, xanchor='left', align='left', showarrow=False,
                       text='Peak in number of cases')
    fig.update_layout(shapes=[
        dict(
          type= 'line', line_color='gray', line_dash='dash',
          yref= 'paper', y0= 0, y1= 1,
          xref= 'x', x0='24-Jan', x1='24-Jan',
        ),
        dict(
          type= 'line', line_color='gray', line_dash='dash',
          yref= 'paper', y0= 0, y1= 1,
          xref= 'x', x0='1-Nov', x1='1-Nov',
        ),
        ]
    )    

# save as html, with plotly JS library loaded from CDN
fig.write_html(
    file=htmlfile,
    default_height=500,
    default_width=700,
    include_plotlyjs='cdn',
    )   

os.startfile(htmlfile)



fig.write_image(
    save_png,
    width=700,
    height=500,
    engine='kaleido',
)
os.startfile(save_png)



