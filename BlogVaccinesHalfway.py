# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 08:07:05 2021

@author: 212367548
"""

import pandas as pd
import datetime
from plotly.offline import plot as pplot
import plotly.express as px
import os

import covid

#%% Vaccination data

# from Our World In Data github, recording CDC data

vax_github = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv'
vax_df = pd.read_csv(vax_github, converters={'date': pd.to_datetime})

# vax_offline = 'data/vaccinations/us_state_vaccinations.csv'
# vax_df = pd.read_csv(vax_offline, converters={'date': pd.to_datetime})

vax_wi = vax_df[vax_df.location == 'Wisconsin']

daily = vax_wi.set_index('date').drop('location', axis=1).diff()
avg7 = daily.rolling(7).mean()

#%% Plots

vax_wi.plot(x='date', y=['total_distributed', 'total_vaccinations'])
vax_wi.plot(x='date', y='share_doses_used')
vax_wi.plot(x='date', y=['people_fully_vaccinated_per_hundred', 'people_vaccinated_per_hundred'])

daily.plot(y=['total_distributed', 'total_vaccinations'])

#%% Plot vax by age group from WI DHS data

vax_age_file = 'data\\vaccinations\\Vax-Age-WI.csv'

vax_age = pd.read_csv(vax_age_file, converters={'Reporting date': pd.to_datetime})

vax_age.pivot(index='Reporting date', columns='Age group', values='Initiated %').plot()

#%% Same for race
vax_race_file = 'data\\vaccinations\\Vax-Race-WI.csv'

vax_race = pd.read_csv(vax_race_file, converters={'Reporting date': pd.to_datetime})

vax_race.pivot(index='Reporting date', columns='Race', values='Initiated %').plot()
