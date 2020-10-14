# -*- coding: utf-8 -*-
"""
Work on positivity rate

Comparing positivity rate for new persons, vs. all tests
"""
# path = 'C:/dev/Covid/'
path = './'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import covid
import urllib
from scipy import signal
import datetime
import os


#%% Get the data

datapath = '.\\data'
csv_file_pop = os.path.join(datapath, 'Population-Data-WI.csv')
# covid.download_pop_data_wi(csv_file_pop)
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.read_covid_data_wi('state')


#%% Work on adjust cases for testing

select = covid.select_data(widata, 'WI', ['POS_NEW', 'TEST_NEW', 'DTH_NEW'])
cases = select['POS_NEW'].rolling(window=7, center=False).mean()
tests = select['TEST_NEW'].rolling(window=7, center=False).mean()
deaths = select['DTH_NEW'].rolling(window=7, center=False).mean()

# back-date tests by 7 days to account for  reporting delays? doesn't seem to make much difference
# tests.index = tests.index - datetime.timedelta(days=7)

est = pd.DataFrame({'cases': cases, 'tests': tests, 'deaths': deaths})

est['Case prevalence'] = est['cases'] / popdata['WI']
est['Detected prevalence'] = est['Case prevalence'] * 15
est['Positive rate'] = est['cases'] / est['tests']
est['Estimated infection prevalence'] = np.sqrt(est['Positive rate'] * est['Case prevalence'])

est.plot(y=['Detected prevalence', 'Estimated infection prevalence'])

est.plot(y='Positive rate')




#%% Compare to Youyang Gu's WI estimate

gu_ifr_file = '..\covid19_projections\implied_ifr\IIFR_US_WI.csv'
    
# read CSV data into a DataFrame, then convert to a Series
gudata = pd.read_csv(gu_ifr_file)
gudata['Date'] = pd.to_datetime(gudata['date']) + datetime.timedelta(days=14)
gudata = gudata.set_index('Date')


est['Gu Estimate'] = gudata['true_inf_est_7day_ma']
est['Bayer Estimate'] = est['Estimated infection prevalence'] * popdata['WI'] / 7
est['Detected x10'] = est['cases'] * 10
est['Detected Cases'] = est['cases']

# back-dated deaths, assume IFR 1%
deaths = select['DTH_NEW'].rolling(window=7, center=False).mean()
deaths.index = deaths.index - datetime.timedelta(days=14)
est['Deaths (IFR 0.75%, 14 day shift)'] = deaths * 150

est.plot(title='Wisconsin New Infection Estimates', y=['Detected Cases', 'Gu Estimate', 'Bayer Estimate', 'Deaths (IFR 0.75%, 14 day shift)'])

est.plot(title='Wisconsin New Infection Estimates', y=['Detected Cases', 'Gu Estimate', 'Bayer Estimate'])



