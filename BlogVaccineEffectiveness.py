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
import numpy as np
import covid

from tableauscraper import TableauScraper as TS
ts = TS()  


#%% Load population

pop_age = covid.read_pop_age_wi('vax')

#%% Load in age tables for all outcomes

datasets = ['Cases', 'Hospitalizations', 'Deaths']

urls = {'Cases': 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatusAge/Cases?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link',
        'Hospitalizations': 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatusAge/Hospitalizations?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link',
        'Deaths': 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatusAge/Deaths?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link',
        }

vax_age_all = pd.DataFrame()

for outcome in datasets:
    
    ts.loads(urls[outcome])
    dashboard = ts.getWorkbook()
    vax_age = dashboard.getWorksheet(outcome + ' by Age').data
    
    vax_age = vax_age.pivot(index='Age group-value', columns='Measure Names-alias', values='Measure Values-alias')
    vax_age.columns.name = 'Vax status'
    vax_age.index.name = 'Age group'
    col_rename = {'Percent of people who completed the vaccine series by the middle of the month': 'Vax fraction',
                  'Rate of ' + outcome.lower() + ' per 100,000 fully vaccinated people': 'Vax',
                  'Rate of ' + outcome.lower() + ' per 100,000 not fully vaccinated people': 'Unvax'}
    vax_age = vax_age.rename(columns=col_rename)
    vax_age['Vax fraction'] = pd.to_numeric(vax_age['Vax fraction'].str.replace('%',''))/100
    vax_age['Vax'] = pd.to_numeric(vax_age.Vax.str.replace(',',''))
    vax_age['Unvax'] = pd.to_numeric(vax_age.Unvax.str.replace(',',''))
    
    # get to a flatter format
    vax_frac = vax_age['Vax fraction']
    vax_age = vax_age.reset_index().melt(id_vars=['Age group', 'Vax fraction'], value_name=outcome)
    vax_age['Age group population'] = vax_age['Age group'].apply(lambda p: pop_age[p]) 
    vax_age['Population'] = (vax_age['Age group population'] * vax_age['Vax fraction'] * (vax_age['Vax status'] == 'Vax')
        + vax_age['Age group population'] * (1-vax_age['Vax fraction']) * (vax_age['Vax status'] == 'Unvax') )
    
    # get rid of intermediate calculation columns
    vax_age = vax_age.drop(['Age group population', 'Vax fraction'], axis=1)
    
    # merge the new data with the previous data 
    vax_age_all[vax_age.columns] = vax_age
    
# put columns in the right order
vax_age_all = vax_age_all[['Age group', 'Vax status', 'Population', 'Cases', 'Hospitalizations', 'Deaths']]



#%% Settings for all plots


# get age group labels from pop_age
labels = list(pop_age.index)
labels.remove('Total')

color = {'Cases': 'steelblue',
         'Hospitalizations': 'darkorange',
         'Deaths': 'firebrick'}

pattern = {'Vax': '/', 'Unvax': ''}

#%% simplify - variable width graph - stratified by age
# based loosely on mekko example from plotly documentation https://plotly.com/python/bar-charts/

# select outcome
outcome = datasets[2]

# select age groups to include
vax_age = vax_age_all[vax_age_all['Age group']!='Total']

# select ordering of Vax status / age group
vax_age = vax_age.sort_values(['Vax status', 'Age group'], ascending=[False, True])



# x values of bars - based on population as width
vax_age['x'] = vax_age.Population.cumsum() - vax_age.Population


fig = go.Figure()
for status in ['Vax', 'Unvax']:
    data = vax_age[vax_age['Vax status']==status]
        
    fig.add_trace(go.Bar(
        name=status,
        y=data[outcome],
        x=data['x'],
        width=data['Population'],
        offset=0,
        marker_color=color[outcome],
        marker_pattern_shape=pattern[status],
        customdata=np.transpose([data['Age group'], data[outcome]*data.Population/1e5]),
        # texttemplate="%{y} x %{width} =<br>%{customdata[1]}",
        # textposition="inside",
        # textangle=0,
        # textfont_color="white",
        hovertemplate="<br>".join([
            "%{customdata[0]}",
            "Population: %{width}",
            outcome + 'per 100k: %{y}',
            "Total " + outcome + ": %{customdata[1]}",
        ])
    ))

fig.update_xaxes(
    tickvals = vax_age.Population.cumsum() - vax_age.Population/2,
    ticktext = vax_age['Age group']
)

# fig.update_xaxes(range=[0,100])
# fig.update_yaxes(range=[0,100])

fig.update_layout(
    title_text = outcome + " by Age and Vax - Testing",
    uniformtext=dict(mode="hide", minsize=10),
)

savefile = '.\\docs\\assets\\plotly\\VaxBarAge.html'
fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)

#%% variable width graph - stratified by age
# based loosely on mekko example from plotly documentation https://plotly.com/python/bar-charts/

outcome = datasets[2]

vax_age = vax_age_all[outcome]

vax_frac = vax_age.loc[labels, 'Vax fraction']

widths = {'Vax': vax_frac * pop_age[labels],
          'Unvax': (1-vax_frac) * pop_age[labels]}

widths_total = widths['Vax'] + widths['Unvax']

data = {
    "Vax": vax_age.loc[labels, 'Vax'],
    "Unvax": vax_age.loc[labels, 'Unvax']
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
        marker_color=color[outcome],
        marker_pattern_shape=pattern[key],
        # customdata=np.transpose([labels, widths[key]*data[key]]),
        # texttemplate="%{y} x %{width} =<br>%{customdata[1]}",
        # textposition="inside",
        # textangle=0,
        # textfont_color="white",
        hovertemplate="<br>".join([
            "label: %{customdata[0]}",
            "width: %{width}",
            "height: %{y}",
            "area: %{customdata[1]}",
        ])
    ))

fig.update_xaxes(
    tickvals=np.cumsum(widths_total)-widths_total/2,
    # ticktext= ["%s<br>%d" % (l, w) for l, w in zip(labels, widths_total)]
    ticktext= labels
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

#%% vax/unvax no age
# based loosely on mekko example from plotly documentation https://plotly.com/python/bar-charts/

outcome = datasets[2]

vax_age = vax_age_all[outcome]

labels = 'Total'

vax_frac = vax_age.loc[labels, 'Vax fraction']

widths = {'Vax': vax_frac * pop_age[labels],
          'Unvax': (1-vax_frac) * pop_age[labels]}

widths_total = widths['Vax'] + widths['Unvax']

data = {
    "Vax": vax_age.loc[labels, 'Vax'],
    "Unvax": vax_age.loc[labels, 'Unvax']
}



fig = go.Figure()
for key in data:
    # x = np.cumsum(widths_total) - widths['Unvax']
    # if key == 'Vax':
    #     x = x - widths['Vax']
        
    x = np.cumsum(widths[key]) - widths[key]
    if key == 'Unvax':
        x = x + widths['Vax'].sum()
        
    fig.add_trace(go.Bar(
        name=key,
        y=[data[key]],
        x=x,
        width=[widths[key]],
        offset=0,
        marker_color=color[outcome],
        marker_pattern_shape=pattern[key],
        # customdata=np.transpose([labels, widths[key]*data[key]]),
        # texttemplate="%{y} x %{width} =<br>%{customdata[1]}",
        # textposition="inside",
        # textangle=0,
        # textfont_color="white",
        hovertemplate="<br>".join([
            "label: %{customdata[0]}",
            "width: %{width}",
            "height: %{y}",
            "area: %{customdata[1]}",
        ])
    ))

# fig.update_xaxes(
#     tickvals=np.cumsum(widths_total)-widths_total/2,
#     # ticktext= ["%s<br>%d" % (l, w) for l, w in zip(labels, widths_total)]
#     ticktext= labels
# )

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


#%% vax/unvax total with age superimposed
# based loosely on mekko example from plotly documentation https://plotly.com/python/bar-charts/

outcome = datasets[2]

vax_age = vax_age_all[outcome]

labels = 'Total'

vax_frac = vax_age.loc[labels, 'Vax fraction']

widths = {'Vax': vax_frac * pop_age[labels],
          'Unvax': (1-vax_frac) * pop_age[labels]}

widths_total = widths['Vax'] + widths['Unvax']

data = {
    "Vax": vax_age.loc[labels, 'Vax'],
    "Unvax": vax_age.loc[labels, 'Unvax']
}



fig = go.Figure()
for key in data:
    # x = np.cumsum(widths_total) - widths['Unvax']
    # if key == 'Vax':
    #     x = x - widths['Vax']
        
    x = np.cumsum(widths[key]) - widths[key]
    if key == 'Unvax':
        x = x + widths['Vax'].sum()
        
    fig.add_trace(go.Bar(
        name=key,
        y=[data[key]],
        x=x,
        width=[widths[key]],
        offset=0,
        marker_color=color[outcome],
        marker_pattern_shape=pattern[key],
        marker_opacity=0.4,
        # customdata=np.transpose([labels, widths[key]*data[key]]),
        # texttemplate="%{y} x %{width} =<br>%{customdata[1]}",
        # textposition="inside",
        # textangle=0,
        # textfont_color="white",
        hovertemplate="<br>".join([
            "label: %{customdata[0]}",
            "width: %{width}",
            "height: %{y}",
            "area: %{customdata[1]}",
        ])
    ))

# fig.update_xaxes(
#     tickvals=np.cumsum(widths_total)-widths_total/2,
#     # ticktext= ["%s<br>%d" % (l, w) for l, w in zip(labels, widths_total)]
#     ticktext= labels
# )

# fig.update_xaxes(range=[0,100])
# fig.update_yaxes(range=[0,100])


labels = list(pop_age.index)
labels.remove('Total')
vax_frac = vax_age.loc[labels, 'Vax fraction']

widths = {'Vax': vax_frac * pop_age[labels],
          'Unvax': (1-vax_frac) * pop_age[labels]}

widths_total = widths['Vax'] + widths['Unvax']

data = {
    "Vax": vax_age.loc[labels, 'Vax'],
    "Unvax": vax_age.loc[labels, 'Unvax']
}


for key in data:
    # x = np.cumsum(widths_total) - widths['Unvax']
    # if key == 'Vax':
    #     x = x - widths['Vax']
        
    x = np.cumsum(widths[key]) - widths[key]
    if key == 'Unvax':
        x = x + widths['Vax'].sum()
        
    fig.add_trace(go.Bar(
        name=key,
        y=data[key],
        x=x,
        width=widths[key],
        offset=0,
        marker_color=color[outcome],
        marker_pattern_shape=pattern[key],
        # customdata=np.transpose([labels, widths[key]*data[key]]),
        # texttemplate="%{y} x %{width} =<br>%{customdata[1]}",
        # textposition="inside",
        # textangle=0,
        # textfont_color="white",
        hovertemplate="<br>".join([
            "label: %{customdata[0]}",
            "width: %{width}",
            "height: %{y}",
            "area: %{customdata[1]}",
        ])
    ))












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


#%% variable width graph - grouped by vax/unvax
# based loosely on mekko example from plotly documentation https://plotly.com/python/bar-charts/

outcome = datasets[2]

vax_age = vax_age_all[outcome]

vax_frac = vax_age.loc[labels, 'Vax fraction']

widths = {'Vax': vax_frac * pop_age[labels],
          'Unvax': (1-vax_frac) * pop_age[labels]}

widths_total = widths['Vax'] + widths['Unvax']

data = {
    "Vax": vax_age.loc[labels, 'Vax'],
    "Unvax": vax_age.loc[labels, 'Unvax']
}



fig = go.Figure()
for key in data:
    # x = np.cumsum(widths_total) - widths['Unvax']
    # if key == 'Vax':
    #     x = x - widths['Vax']
        
    x = np.cumsum(widths[key]) - widths[key]
    if key == 'Unvax':
        x = x + widths['Vax'].sum()
        
    fig.add_trace(go.Bar(
        name=key,
        y=data[key],
        x=x,
        width=widths[key],
        offset=0,
        marker_color=color[outcome],
        marker_pattern_shape=pattern[key],
        # customdata=np.transpose([labels, widths[key]*data[key]]),
        # texttemplate="%{y} x %{width} =<br>%{customdata[1]}",
        # textposition="inside",
        # textangle=0,
        # textfont_color="white",
        hovertemplate="<br>".join([
            "label: %{customdata[0]}",
            "width: %{width}",
            "height: %{y}",
            "area: %{customdata[1]}",
        ])
    ))

fig.update_xaxes(
    tickvals=np.cumsum(widths_total)-widths_total/2,
    # ticktext= ["%s<br>%d" % (l, w) for l, w in zip(labels, widths_total)]
    ticktext= labels
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




#%%
exit


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
