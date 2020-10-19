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
test_file = "data\\By_Test_Data_data_2020-10-19.csv"
test = pd.read_csv(test_file)

test = test[test['Measure Names']=='Positive tests']

col_rename = {'Day of displaydateonly': 'Date', 'Positives': 'Positives', 'Totals': 'Tests' }

test = test[col_rename.keys()]
test = test.rename(columns=col_rename)
test['Date'] = pd.to_datetime(test['Date'])
test = test.set_index('Date')

# test.plot(y=['Positives','Tests'])

#%% By People
# cases and new people tested
people_file = "data\\By_Person_Data_data_2020-10-19.csv"
people = pd.read_csv(people_file)

people = people[people['Measure Names']=='People tested positive']

col_rename = {'Day of Result Date': 'Date', 'Positive.y': 'Cases', 'Total.Y': 'New people tested' }

people = people[col_rename.keys()]
people = people.rename(columns=col_rename)
people['Date'] = pd.to_datetime(people['Date'])
people = people.set_index('Date')

# people.plot(y=['Cases', 'New people tested'])


#%% Deaths by death date
deaths_file = "data\\Deaths by day_crosstab_2020-10-14.csv"
deaths_raw = pd.read_csv(deaths_file)
# Note: key is to download the file and then re-save it in Excel specifically
# as csv, otherwise it's actually tab delimited and harder to read in in python

deaths = pd.DataFrame(dict(Date=deaths_raw.T.iloc[2:,0],
                           Deaths=deaths_raw.T.iloc[2:,1],
                           Prelim=deaths_raw.T.iloc[2:,2]))
         
# date leaves out the year, so suffix it properly, then convert to datetime       
deaths.Date = deaths.Date.astype(str) + '-2020'            
deaths.Date = pd.to_datetime(deaths.Date)
deaths = deaths.set_index('Date')

# make sure everything's numeric
deaths.Deaths = pd.to_numeric(deaths.Deaths)
deaths.Prelim = pd.to_numeric(deaths.Prelim)


#%% Compare cases, tests, deaths by date to as-reported

people['Cases Reported'] = widata.set_index('Date').POS_NEW
people['Tests Reported'] = widata.set_index('Date').TEST_NEW
deaths['Reported'] = widata.set_index('Date').DTH_NEW

people.plot(y=['Cases', 'Cases Reported'])
people.plot(y=['New people tested', 'Tests Reported'])
deaths.plot(y=['Deaths', 'Reported'])

#%% Estimate true new cases

people['CaseAvg'] = people.Cases.rolling(window=7, center=False).mean()
test['PosAvg'] = test.Positives.rolling(window=7, center=False).mean()
test['TestAvg'] = test.Tests.rolling(window=7, center=False).mean()
deaths['DeathAvg'] = deaths.Deaths.rolling(window=7, center=False).mean()

test.plot(y=['PosAvg', 'TestAvg'])

est = pd.DataFrame({'cases': people.CaseAvg, 'positives': test.PosAvg, 'tests': test.TestAvg, 'deaths': deaths.DeathAvg})

inf_const = 1/10

est['infections'] = inf_const * est['cases'] * np.sqrt(popdata['WI'] / est['tests'])

est.plot(y=['cases','infections'])



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












