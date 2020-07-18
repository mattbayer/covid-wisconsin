# -*- coding: utf-8 -*-
"""
Work on Coronavirus data analysis

Script for downloading, parsing, plotting Covid data from Wisconsin.
"""
path = 'C:/dev/Covid/'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import covid
import urllib
from scipy import signal


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


covid.plot_by_county(widata, popdata, 'POS_NEW', 9)
# covid.plot_by_county(widata, popdata, 'DTH_NEW', 6)


#%% 
# covid.plotDCT(widata, 'WI')
covid.plotDCT(widata, ['WI', 'Milwaukee', 'Sheboygan', 'Brown', 'Dane', 'La Crosse'], per_capita=True, popdata=popdata)




#%% Plot age distribution
# Note - this data is not present for counties.  Only data broken out by 
# county is deaths, cases, tests.

# Make new columns for *new* positives in age brackets
age_suffix = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_59', '60_69', '70_79', '80_89', '90']
cumul_cols = ['POS_' + sfx for sfx in age_suffix]  
new_cols = ['POS_NEW_' + sfx for sfx in age_suffix]

select = covid.select_data(widata, 'WI', cumul_cols)

select[new_cols] = select[cumul_cols].diff()
# first 7-day boxcar average for weekly effects, then 5-day hamming to smooth
avg = select.rolling(window=7, center=True).mean()
avg = avg.rolling(window=5, win_type='hamming', center=True).mean()
    
# avg.plot.area(y=new_cols)
avg.plot(y=new_cols)

# Statement to compute new positives for all counties, before I realized 
# the data wasn't there.  Functions are still useful to learn.
# widata[new_cols] = widata.groupby('NAME')[cumul_cols].diff()

#%% Plot hospitalization status

select = covid.select_data(widata, 'WI', ['POSITIVE', 'HOSP_YES', 'HOSP_NO', 'HOSP_UNK'])

select['HOSP_NEW'] = select['HOSP_YES'].diff()

avg = select.rolling(window=7, center=True).mean()
avg.plot(y='HOSP_NEW')


#%% Try to estimate true prevalence


loc = 'WI'
select = covid.select_data(widata, loc)
avg = select.rolling(window=7, center=True).mean()    

# offset tests by ten days?
cases = avg.POS_NEW
tests = avg.TEST_NEW
# tests.index -= pd.DateOffset(days=10)



pos_rate = cases/tests
plt.figure()
plt.plot(tests, pos_rate, '.:')


plt.figure()
plt.plot(cases*10)
plt.plot(tests)
plt.plot(500 * cases / np.sqrt(tests))

#%% Try correcting for test result reporting postponement by forward convolving

t = tests.to_numpy().copy()
# fill in NaNs at the end with copies
t[-3:] = t[-4]
t[0:4] = t[4]

# two sided exponential
k = 7
x0 = 8
n = 20
r = np.concatenate((np.arange(1,n-x0), np.arange(n-x0,n-2*x0-1,-1)))
test_response = np.exp(r/k)
test_response = test_response / np.sum(test_response)

t = np.concatenate((t, np.ones(n)*t[-1]))
x = np.arange(0,len(t))
t2 = signal.convolve(t, test_response, 'valid')
x2 = np.arange(0,len(t2))
  
    
plt.figure()
plt.plot(x,t)
plt.plot(x2, t2)

#%% Similar plots with modified test curve

tests2 = pd.Series(data=t2[0:-1], index=tests.index)

pos_rate2 = cases/tests2
plt.figure()
plt.plot(tests2, pos_rate2, '.:')


plt.figure()
plt.plot(cases*10)
plt.plot(tests2)
plt.plot(500 * cases / np.sqrt(tests2))

#%% Try deconvolving with some kind of reporting response
# Doesn't seem to work very well.

# test_response = np.arange(14, 0, -1)
# test_response[0] *= 2
# test_response = np.ones(10)
# test_response = signal.windows.triang(11)
test_response = np.exp(-np.arange(0,11)/5)
test_response = test_response / np.sum(test_response)
t = tests.to_numpy()
x = np.arange(0,len(t))
t[np.isnan(t)] = 0
recovered, remainder = signal.deconvolve(t, test_response)
plt.figure()
plt.plot(t)
plt.plot(recovered)
plt.plot(remainder)





