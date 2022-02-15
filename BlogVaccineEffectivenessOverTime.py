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


#%% Plots of relative risk by month

fig = px.line(
    vax, 
    x='Month',
    y='Relative risk',
    color='Outcome',
    color_discrete_sequence=['steelblue', 'darkorange', 'firebrick'],
    markers=True,
    )

savefile = '.\\docs\\assets\\plotly\\VaxEfficacyTime.html'
fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)

#%% Load all the saved data

months = list(range(8,12))  # months 8:11 inclusive

for m in months:
    filestr = 'Breakthroughs_2021-' + str(m).zfill(2) + '.csv'
    print(filestr)
    
    
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
