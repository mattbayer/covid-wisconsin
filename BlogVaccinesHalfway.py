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

# from Our World In Data github

# vax_github = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv'
# vax_df = pd.read_csv(vax_github)

vax_offline = 'data/vaccinations/us_state_vaccinations.csv'
vax_df = pd.read_csv(vax_offline)

vax_wi = vax_df[vax_df.location == 'Wisconsin']
vax_wi.date = pd.to_datetime(vax_wi.date.copy())

daily = vax_wi.set_index('date').drop('location', axis=1).diff()
avg7 = daily.rolling(7).mean()

#%% Plots

vax_wi.plot(x='date', y=['total_distributed', 'total_vaccinations'])
vax_wi.plot(x='date', y='share_doses_used')

daily.plot(y=['total_distributed', 'total_vaccinations'])
