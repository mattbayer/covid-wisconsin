# -*- coding: utf-8 -*-
"""
Work on Coronavirus data analysis

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
# Updated by UpdateData.py, just load from csv here

csv_file_covid = path + 'Covid-Data-WI.csv'
csv_file_pop = path + 'Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.read_covid_data_wi(csv_file_covid)



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

# back-dated deaths, assume IFR 1%
deaths = select['DTH_NEW'].rolling(window=7, center=False).mean()
deaths.index = deaths.index - datetime.timedelta(days=14)
est['Deaths (IFR 0.75%)'] = deaths * 150

est.plot(title='Wisconsin New Infection Estimates', y=['Detected x10', 'Gu Estimate', 'Bayer Estimate', 'Deaths (IFR 0.75%)'])



#%% Work on hospitalization status

select = covid.select_data(widata, 'WI', ['POS_NEW', 'DTH_NEW', 'HOSP_YES', 'HOSP_NO', 'HOSP_UNK'])

select['New Hospitalizations'] = select['HOSP_YES'].diff()
select['New Not Hosp'] = select['HOSP_NO'].diff()
select['New Hosp Unknown'] = select['HOSP_UNK'].diff()
select['New Hosp Known'] = select['New Hospitalizations'] + select['New Not Hosp']

# for plotting next to hospitalizations
select['Cases / 10'] = select['POS_NEW'] / 10

select = select.rolling(window=7, center=True).mean()


# actually should average before this point
select['Percent Hosp'] = select['New Hospitalizations'] / select['POS_NEW']
select['Percent Not Hosp'] = select['New Not Hosp'] / select['POS_NEW']
select['Percent Hosp Unknown'] = select['New Hosp Unknown'] / select['POS_NEW']
select['Percent Hosp Known'] = 1 - select['Percent Hosp Unknown']
select['Percent Hosp of Known'] = select['New Hospitalizations'] / select['New Hosp Known']
select['Percent Not of Known'] = select['New Not Hosp'] / select['New Hosp Known']


# hospitalizations estimate
# Assume hospitalized % in the unknown portion is the same as in the known portion
# On the other hand, it would seem like unknowns would be more likely
# to be non-hospitalized.  So this estimate is probably an upper bound. But it
# does seem to smooth out the hospitalization curve.
# I'm not entirely convinced by this - the case peak I think is mainly from testing
# still shows up as a hospitalization peak - but I'm not sure where else to go with it now.
# select['New Hosp Estimate'] = select['POS_NEW'] * select['Percent Hosp of Known']
# second version with arbitrary factor
select['New Hosp Estimate'] = select['New Hospitalizations'] + 0.5 * select['POS_NEW'] * select['Percent Hosp Unknown'] * select['Percent Hosp of Known']
# another idea could be to normalize the corrected curve to have the same total,
# on the theory that we are getting all of them eventually, but we need to correct
# for variations in reporting.  Maybe that would work?

avg = select
# avg = select.rolling(window=7, center=True).mean()
# avg.plot(y=['HOSP_YES', 'HOSP_NO', 'HOSP_UNK'])

avg.plot(y=['DTH_NEW', 'New Hospitalizations', 'New Hosp Estimate', 'Cases / 10'])
avg.plot(y=['Percent Hosp', 'Percent Not Hosp', 'Percent Hosp Unknown'], kind='area')
avg.plot(y=['Percent Hosp', 'Percent Hosp of Known', 'Percent Not Hosp', 'Percent Not of Known', 'Percent Hosp Known'])
#

avg['Cases / 1000'] = avg['Cases / 10']/100
avg['Hosp / 100'] = avg['New Hospitalizations']/100
avg.plot(y=['Percent Hosp', 'Percent Not Hosp', 'Percent Hosp Known', 'Percent Hosp of Known', 'Hosp / 100', 'Cases / 1000'])





