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





