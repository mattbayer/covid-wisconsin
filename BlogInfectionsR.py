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
test_file = "data\\By_Test_Data_data_2021-02-12.csv"

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

#%% Estimate infections
Npop = popdata['WI']
Npos = alldata['Positives smoothed']
Ntests = alldata['Tests smoothed']

D1 = 3
alpha = 0.6

alldata['Infections (Power)'] = 1/D1 * alldata['Positives smoothed'] * np.power(Npop/Ntests, 1-alpha)

# revised formula to take account of previously detected cases being taken
# out of the testing pool

D2 = 15
alpha = 0.4
alldata['Dedup factor'] = 1 + 1/D2 * (np.power(Npop/Ntests, 1-alpha) - 1)
alldata['Infections (Dedup)'] = Npos * alldata['Dedup factor']


alldata.plot(y=['Positives smoothed', 'Infections (Power)', 'Infections (Dedup)'])
alldata.plot(y=['Positives smoothed', 'Infections (Power)', 'Infections (Dedup)'], logy=True)

alldata['Infections'] = alldata['Infections (Dedup)']

# to an extent I may be overfitting
# D=3, alpha=0.6 on Power is very close to D=15,alpha=0.4 for Dedup.  So to an 
# extent these formulas are not unique.
# However, given that D actually means something, supposedly, Dedup is better
# because it gives good results at reasonable D (the length that someone is PCR
# positive).  Then the only changeable parameter is alpha, instead of two 
# changeable parameters.

#%% Cumulative 

alldata['Total Infected % (Dedup)'] = alldata['Infections (Dedup)'].sort_index().cumsum()/Npop*100
alldata['Total Infected % (Power)'] = alldata['Infections (Power)'].sort_index().cumsum()/Npop*100
alldata['Total Positive %'] = alldata['Positives'].sort_index().cumsum()/Npop*100

antibody_dates = [datetime.datetime(2020, 6, 30, 0, 0), datetime.datetime(2020, 11, 1, 0, 0)]
antibody_perc  = [1.6, 7.0]

antibody = pd.DataFrame(data={'Antibody survey': antibody_perc}, index=antibody_dates)
antibody['Antibody survey x2'] = antibody['Antibody survey'] * 2

alldata.plot(y=['Total Infected % (Dedup)', 'Total Infected % (Power)', 'Total Positive %'])

plt.plot(antibody.index, antibody['Antibody survey'], label='Antibody survey')   
plt.plot(antibody.index, antibody['Antibody survey x2'], label='Antibody survey x2')   


#%% Compare with deaths

# Create an aligned deaths column
IFR = 0.0045
lag = 10
deaths_aligned = alldata['Deaths smoothed'] / IFR
deaths_aligned = deaths_aligned.reset_index()
deaths_aligned.Date = deaths_aligned.Date - datetime.timedelta(days=lag)
deaths_aligned = deaths_aligned.set_index('Date')
alldata['Deaths aligned'] = deaths_aligned

alldata.plot(y=['Deaths smoothed', 'Positives smoothed', 'Infections', 'Deaths aligned'], logy=True)
alldata.plot(y=['Deaths smoothed', 'Positives smoothed', 'Infections', 'Deaths aligned'], logy=False)
# alldata.plot(y='Deaths smoothed', logy=False)




#%%
quit


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


      
    






