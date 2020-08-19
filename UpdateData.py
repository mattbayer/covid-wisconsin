# -*- coding: utf-8 -*-
"""
Update Coronavirus data for Wisconsin and make standard plots

Script for downloading, parsing, plotting Covid data from Wisconsin.
"""
# path = 'C:/dev/Covid/'
path = './'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import covid
import urllib
from scipy import signal
import datetime


#%% Get the data
# First retrieve data from server and save to csv file
# Second read data from the previously saved csv file
# comment sections if no need to re-download    

csv_file_covid = path + 'Covid-Data-WI.csv'
csv_file_pop = path + 'Population-Data-WI.csv'

# population data
# covid.download_pop_data_wi(csv_file_pop)
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
covid.download_covid_data_wi(csv_file_covid)
widata = covid.read_covid_data_wi(csv_file_covid)


#%% Plot cases and deaths for the state

# use seaborn theme for plotting
# sns.set()

# covid.plot_tests_posrate(widata, 'WI')
# covid.plot_cases_deaths(widata, 'WI')
# covid.plot_cases_tests(widata, 'WI')

covid.plot_cases_posrate(widata, 'WI')

#%% Plot by county

covid.plot_by_county(widata, popdata, 'POS_NEW', 9)
# covid.plot_by_county(widata, popdata, 'DTH_NEW', 6)

#%% Sort by county cases per-capita
# sort by per-capita new cases
pivot = widata.pivot(index='Date', columns='NAME', values='POS_NEW')
avg = pivot.rolling(window=7, center=False).mean()
capita = covid.convert_per_capita(avg, popdata)
counties = capita.columns
last_value = capita.iloc[-1]
sort_order = last_value.sort_values(ascending=False)

print(sort_order.index[0:10])

covid.plotDCT(widata, ['WI', 'Milwaukee', 'Waukesha', 'Kenosha', 'Racine', 'Walworth'], per_capita=True, popdata=popdata)



#%% Plot deaths, cases, tests
covid.plotDCT(widata, 'WI')
covid.plotDCT(widata, ['WI', 'Milwaukee', 'Dane', 'Brown'], per_capita=True, popdata=popdata)

# covid.plotDCT(widata, ['WI', 'Milwaukee', 'Sheboygan', 'Brown', 'Dane', 'La Crosse'], per_capita=True, popdata=popdata)


#%% Plot age distribution
# Note - this data is not present for counties.  Only data broken out by 
# county is deaths, cases, tests.
covid.plot_by_age(widata)


# Statement to compute new positives for all counties, before I realized 
# the data wasn't there.  Functions are still useful to learn.
# widata[new_cols] = widata.groupby('NAME')[cumul_cols].diff()
