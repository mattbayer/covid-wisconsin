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

#%% By Test

# manually downloaded file - positives and tests
test_file = "data\\By_Test_Data_data_2021-01-22.csv"

test = covid.read_bytest_wi(test_file)

test = test.set_index('Date')


#%% Deaths by death date
deaths_file = "data\\Deaths by day stacked_2021-02-09.csv"
deaths= covid.read_deathdate_wi(deaths_file)

deaths = deaths.set_index('Date')



#%% Compare cases, tests, deaths by date to as-reported

alldata = test
alldata['Deaths'] = deaths['Confirmed deaths']
alldata['Cases Reported'] = widata.set_index('Date').POS_NEW
alldata['Deaths Reported'] = widata.set_index('Date').DTH_NEW
 
alldata.plot(y=['Positives', 'Cases Reported'])
alldata.plot(y=['Deaths', 'Deaths Reported'])


#%% Smoothed data
alldata['Deaths smoothed'] = alldata['Deaths'].rolling(window=7, center=True, win_type=None).mean()
alldata['Positives smoothed'] = alldata['Positives'].rolling(window=7, center=True, win_type=None).mean()
alldata['Tests smoothed'] = alldata['Tests'].rolling(window=7, center=True, win_type=None).mean()
alldata['Deaths x200'] = alldata['Deaths smoothed'] * 200

#%% Estimate infections
inf_const = 1/10
alpha = 0.4

alldata['Infections'] = inf_const * alldata['Positives smoothed'] * np.power(popdata['WI'] / alldata['Tests smoothed'], 1-alpha)

#%% Plot cases/deaths on log scale

alldata.plot(y=['Deaths smoothed', 'Positives smoothed', 'Infections', 'Deaths x200'], logy=True)
# alldata.plot(y='Deaths smoothed', logy=False)

#%% Estimate true new cases

people['CaseAvg'] = people.Cases.rolling(window=7, center=False).mean()
test['PosAvg'] = test.Positives.rolling(window=7, center=False).mean()
test['TestAvg'] = test.Tests.rolling(window=7, center=False).mean()
deaths['DeathAvg'] = deaths.Deaths.rolling(window=7, center=False).mean()

test.plot(y=['PosAvg', 'TestAvg'])

est = pd.DataFrame({'cases': people.CaseAvg, 'positives': test.PosAvg, 'tests': test.TestAvg, 'deaths': deaths.DeathAvg})




#%% Compare to Youyang Gu's WI estimate

gu_ifr_file = '..\covid19_projections\implied_ifr\IIFR_US_WI.csv'
    
# read CSV data into a DataFrame, then convert to a Series
gudata = pd.read_csv(gu_ifr_file)
gudata['Date'] = pd.to_datetime(gudata['date']) + datetime.timedelta(days=14)
gudata = gudata.set_index('Date')


est['Gu Estimate'] = gudata['true_inf_est_7day_ma']
est['Bayer Estimate'] = est['infections']
est['Detected x10'] = est['cases'] * 10
est['Detected Cases'] = est['cases']

# back-dated deaths, assume IFR 1%
backdate = 16
ifr = 0.5
name = 'Deaths (IFR ' + str(ifr) + '%, ' + str(backdate) + ' day shift)'
deaths_temp = deaths['DeathAvg'].copy()
deaths_temp.index = deaths_temp.index - datetime.timedelta(days=backdate)
est[name] = deaths_temp / ifr * 100

# est.plot(title='Wisconsin New Infection Estimates', y=['Detected Cases', 'Gu Estimate', 'Bayer Estimate', name])

est.plot(title='Wisconsin New Infection Estimates', y=['cases', 'infections', name])

#%% Cumulative 

plt.figure()
plt.plot(people['Cases'].sort_index().cumsum())
plt.plot(est['infections'].cumsum())
plt.plot(datetime.datetime(2020, 6, 30, 0, 0), 93000,'o')

est['Detected cases'] = est['cases']
est['Estimated infections'] = est['infections']
est['Infection / Case Ratio'] = est['infections'] / est['cases']

est.plot(title='Daily True Infection Estimate', y=['Detected Cases', 'Estimated infections'])
est.plot(title='Infection / Case Ratio', y=['Infection / Case Ratio'])

      
    

#%% Improve new infection estimate?
# - revised formula to take account of previously detected cases being taken
# out of the testing pool

duration = 14
D = duration
Npop = 5.8e6
Ncases = est['Detected Cases']
Ntests = est['tests']


est['Dedup factor'] = 1 + 1/D * (np.sqrt(Npop/Ntests) - 1)
est['Infections (Dedup)'] = est['Detected Cases'] * est['Dedup factor']

est.plot(y=['Detected Cases', 'Estimated infections', 'Infections (Dedup)'])





