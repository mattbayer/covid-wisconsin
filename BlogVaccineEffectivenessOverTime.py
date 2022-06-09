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

#%% Parameters for all plots
imwidth = 600
imheight = 450
date_suffix = '2022-04'

#%% Load the age-adjusted table from DHS

datasets = ['Cases', 'Hospitalizations', 'Deaths']

urls = {'Cases': 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus_16303581926310/CasesbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link',
        'Hospitalizations': 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus_16303581926310/HospitalizationsbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link',
        'Deaths': 'https://bi.wisconsin.gov/t/DHS/views/CasesOutcomesbyVaxStatus_16303581926310/DeathsbyVaxStatus?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link',
        }

#%% Fetch and arrange data

data_all = pd.DataFrame()

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
    # print(data)

    data = data.reset_index().melt(id_vars='Month', var_name='Vax status')
    
    # convert Month from string to datetime, and sort
    data.Month = pd.to_datetime(data.Month)
    data = data.sort_values(['Vax status', 'Month'])
    
    # convert value from string to numeric
    data.value = pd.to_numeric(data.value.apply(lambda v: v.replace(',', '')))
    
    # add outcome column
    data['Outcome'] = outcome + ' per 100k'
    
    # append to overall dataframe
    data_all = data_all.append(data)
    
# renumber the indices
data_all = data_all.reset_index(drop=True)


#%% Process to get efficacy
vax = data_all[data_all['Vax status'] == 'Vax'].reset_index(drop=True)
unvax = data_all[data_all['Vax status'] == 'Unvax'].reset_index(drop=True)

vax['Relative risk'] = vax.value / unvax.value


#%% Plots of risk for vax/unvax
# modify month for the sake of the plot
data_all['Plot month'] = data_all.Month + datetime.timedelta(days=15)

fig = px.line(
    data_all,
    x='Plot month',
    y='value',
    line_dash='Vax status',
    color='Outcome',
    color_discrete_sequence=['steelblue', 'darkorange', 'firebrick'],
    facet_row='Outcome',
    title='Covid rates by vax status<br>(Age-adjusted)'
    )


# update x axis range
fig.update_xaxes({'range': [pd.to_datetime('2021-02-17'), pd.to_datetime('2022-01-15')]})

# Name and ticks for x axis
fig.update_xaxes(row=1, title_text='Month')
fig.update_xaxes(showgrid=False, nticks=11)

# turn off y axis matching for the facets
fig.update_yaxes(matches=None)

# Facet labels - on the left
# Change names of left axis label
fig.update_yaxes(row=3, title_text='Cases per 100k')
fig.update_yaxes(row=2, title_text='Hosp per 100k')
fig.update_yaxes(row=1, title_text='Deaths per 100k')
# make all y axis labels in the same spot - hack by setting standoff high but 
# automargin False so the margin doesn't expand with the standoff
fig.update_yaxes(automargin=False, title_standoff=40)

# update right plot titles - just blank
fig.for_each_annotation(lambda a: a.update(text=''))

# # Facet labels - on the right
# # Change names of left axis label
# fig.update_yaxes(title_text=None)

# # update right plot titles - just blank
# fig.for_each_annotation(
#     lambda a: a.update(
#         text=a.text.split("=")[-1],
#         font=dict(size=15),
#         )
#     )



# make the plot stair-step style
# hvh is centered on the x value, hv is starting at the x value
fig.update_traces(line={"shape": 'vh'})


savefile = '.\\docs\\assets\\plotly\\VaxRatesTime.html'
fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)

save_png = '.\\docs\\assets\\VaxRatesTime_'+date_suffix+'.png'
fig.write_image(
    save_png,
    width=700,
    height=600,
    engine='kaleido',
)
os.startfile(save_png)


#%% Plots of relative risk by month

fig = px.line(
    vax, 
    x='Month',
    y='Relative risk',
    color='Outcome',
    color_discrete_sequence=['steelblue', 'darkorange', 'firebrick'],
    # markers=True,
    )

savefile = '.\\docs\\assets\\plotly\\VaxEfficacyTime.html'
fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)

#%% Load all the saved data

years = [2021, 2022]
months = [[8, 9, 10, 11, 12], []]
detailed = pd.DataFrame()

# get per-100k data for each month and append them into one detailed dataframe
for yy, year in enumerate(years):
    for m in months[yy]:
        month_str = str(year) + '-' + str(m).zfill(2)
        filestr = os.path.join('data', 'vaccinations', 'Breakthroughs_' + month_str + '.csv')
        print(filestr)
        
        vax_month = pd.read_csv(filestr, index_col=0)
        vax_month['Month'] = pd.to_datetime(month_str)
        detailed = detailed.append(vax_month)


# melt the outcome columns
detailed = detailed.melt(id_vars=['Month', 'Age group', 'Vax status', 'Population'],
                         value_vars=['Cases', 'Hospitalizations', 'Deaths'],
                         var_name='Outcome', value_name='value')

# renumber index
detailed = detailed.reset_index(drop=True)

# split into vax/unvax for efficacy
vax = detailed[detailed['Vax status'] == 'Vax'].reset_index(drop=True)
unvax = detailed[detailed['Vax status'] == 'Unvax'].reset_index(drop=True)

vax['Relative risk'] = vax.value / unvax.value
    
#%% Plot efficacy by age group
    
#%% Booster dose info
# retrieved from https://covid.cdc.gov/covid-data-tracker/#vaccinations_vacc-people-additional-dose-count-pop65
# on 14-Feb-2022, 8:36pm
# upshot - about 75% of over-65 in WI have a booster; US average only 58%, e.g. Texas 51%.

# total number of people in WI with a booster
N_boost = 2_008_780

# number over 65 with booster
N_boost_65 = 757_863

# percent fully vax w/ booster
P_two_boost = 0.537

# percent fully vax w/ booster, over 65
P_two_boost_65 = 0.789


# total number of people in WI two doses
N_two = 3_738_069

# number over 65 with booster
N_two_65 = 960_823

# percent with two doses
P_two = 0.642

# percent two doses, over 65
P_two_65 = 0.945

# or, just download the csv
cdc_vax = pd.read_csv('data\\vaccinations\\cdc-vax-states_2022-02-14.csv')
cdc_vax = cdc_vax.set_index('State/Territory/Federal Entity')

P_boost_65 = (cdc_vax['Percent of 65+ Pop Fully Vaccinated by State of Residence']/100 
              * cdc_vax['Percent of fully vaccinated people 65+ with booster doses']/100)
