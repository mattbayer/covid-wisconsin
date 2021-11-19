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

#%% Date suffix
date_suffix = '_2021-11-18'

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
    
    # create 12-17 summed age category
    pop_age['12-17'] = pop_age['12-15']+pop_age['16-17']
    vax_age.loc['12-17'] = (vax_age.loc['12-15']*pop_age['12-15'] + vax_age.loc['16-17']*pop_age['16-17']) / (pop_age['12-17'])
    vax_age = vax_age.drop(['12-15', '16-17'])
    vax_age = vax_age.sort_index()
    
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

vax_age_all.to_csv('.\\data\\vaccinations\\Breakthroughs_2021-11.csv')

#%% Compute age-adjusted efficacy

vax = vax_age_all[vax_age_all['Vax status'] == 'Vax']
unvax = vax_age_all[vax_age_all['Vax status'] == 'Unvax']
vax = vax.set_index('Age group')
unvax = unvax.set_index('Age group')

vax['Total population'] = vax['Population'] + unvax['Population']
unvax['Total population'] = vax['Total population']
pop_wi = vax.loc['Total', 'Total population']

vax['Adjusted Deaths'] = vax['Deaths'] * vax['Total population'] / 1e5
unvax['Adjusted Deaths'] = unvax['Deaths'] * unvax['Total population'] / 1e5


print(vax['Adjusted Deaths'].drop('Total').sum() / pop_wi * 1e5)
print(unvax['Adjusted Deaths'].drop('Total').sum() / pop_wi * 1e5)



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


def plotly_vax_age_bar(vax_age, outcome, priority='Age group', group=None):
    # vax_age needs 'Age groups', 'Population', 'Vax status'
    
    # select age groups to include
    if group is None:
        vax_age = vax_age[vax_age['Age group']!='Total']
    else:
        vax_age = vax_age[vax_age['Age group']==group]
        
    # select ordering of Vax status / age group
    if priority == 'Age group':
        vax_age = vax_age.sort_values(['Age group', 'Vax status'], ascending=[True, False])
    else:
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
        
    # add dividers for age groups
    grouped_widths = vax_age.Population.rolling(2).sum()[1::2]
    if group is None and priority=='Age group':
        grouped_edge = grouped_widths.cumsum() - grouped_widths
        grouptext = vax_age['Age group'].unique()
        
        shapes = list()
        for gg, group in enumerate(grouptext):
            fig.add_annotation(
                text=group,
                x=grouped_edge.iloc[gg], xanchor='left', align='left',
                yref='paper', y=1, yanchor='top',  
                textangle=-90, valign='top',
                showarrow=False,
            )
            if gg != 0:
                shapes.append(
                    dict(
                      type= 'line', line_color='lightgray', 
                      yref= 'paper', y0= 0, y1= 1,
                      xref= 'x', x0=grouped_edge.iloc[gg], x1=grouped_edge.iloc[gg],
                    )
                )

        fig.update_layout(shapes=shapes)

        
    fig.update_xaxes(
        title = 'Share of population'
    )
    fig.update_yaxes(
        title = outcome + ' per 100K'
    )
    
    fig.update_xaxes(range=[0,grouped_widths.sum()])
    
    return fig


#%% Parameters for all plots
imwidth = 600
imheight = 450


#%% 65+ straight numbers
fig = go.Figure()
for status in ['Vax', 'Unvax']:
    data = vax_age[vax_age['Vax status']==status]
    data = data[data['Age group']=='65+']
    data['Deaths'] = data['Deaths'] * data['Population'] / 100e3
        
    fig.add_trace(go.Bar(
        name=status,
        y=data[outcome],
        x=[status],
        # width=data['Population'],
        # offset=0,
        marker_color=color[outcome],
        marker_pattern_shape=pattern[status],
        # customdata=np.transpose([data['Age group'], data[outcome]*data.Population/1e5]),
        # texttemplate="%{y} x %{width} =<br>%{customdata[1]}",
        # textposition="inside",
        # textangle=0,
        # textfont_color="white",
        # hovertemplate="<br>".join([
        #     "%{customdata[0]}",
        #     "Population: %{width}",
        #     outcome + 'per 100k: %{y}',
        #     "Total " + outcome + ": %{customdata[1]}",
        # ])
    ))
    
    
fig.update_layout(
    title_text =  "Number of " + outcome.lower() + " by vax status - 65+<br>(NOT GOOD ANALYSIS FOR ILLUSTRATION ONLY)",
    uniformtext=dict(mode="hide", minsize=10),
    )
fig.update_yaxes(title='Deaths')

save_png = '.\\docs\\assets\\VaxBarAge-DeathRaw-65'+date_suffix+'.png'
fig.write_image(
    save_png,
    width=imwidth,
    height=imheight,
    engine='kaleido',
)
os.startfile(save_png)


#%% 65+ only


# select outcome
outcome = 'Deaths'

fig = plotly_vax_age_bar(vax_age_all, outcome, group='65+')

fig.update_layout(
    title_text = 'Rate of ' + outcome.lower() + " by vax status - 65+",
    uniformtext=dict(mode="hide", minsize=10),
    )


save_png = '.\\docs\\assets\\VaxBarAge-Death-65'+date_suffix+'.png'
fig.write_image(
    save_png,
    width=imwidth,
    height=imheight,
    engine='kaleido',
)
os.startfile(save_png)

#%% vax/unvax totals

outcome = 'Deaths'

fig = plotly_vax_age_bar(vax_age_all, outcome, group='Total')

fig.update_layout(
    title_text = outcome + " by vax status - all ages<br>(AGAIN NOT GREAT ANALYSIS BEAR WITH ME)",
    uniformtext=dict(mode="hide", minsize=10),
    )


save_png = '.\\docs\\assets\\VaxBarAge-Death-Total'+date_suffix+'.png'
fig.write_image(
    save_png,
    width=imwidth,
    height=imheight,
    engine='kaleido',
)
os.startfile(save_png)

#%% variable width graph - stratified by age

for outcome in datasets:
    
    fig = plotly_vax_age_bar(vax_age_all, outcome)
    
    fig.update_layout(
        title_text = outcome + " by vax status <i>and</i> age group<br>Oct 2021",
        uniformtext=dict(mode="hide", minsize=10),
        )
    
        
    save_png = '.\\docs\\assets\\VaxBarAge-' + outcome + '-StratAge'+date_suffix+'.png'
    fig.write_image(
        save_png,
        width=700,
        height=imheight,
        engine='kaleido',
    )
    os.startfile(save_png)




#%%
exit


#%% vax/unvax with order priority reversed

outcome = 'Deaths'

fig = plotly_vax_age_bar(vax_age_all, outcome, priority='Vax status')

fig.update_layout(
    title_text = outcome + " by vax status<br>By age group",
    uniformtext=dict(mode="hide", minsize=10),
    )

    
savefile = '.\\docs\\assets\\plotly\\VaxBarAge-Death-StratAgeVaxGroup.html'
fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)

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
