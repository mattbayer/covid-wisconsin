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
import seaborn as sns
import covid
import urllib
from scipy import signal
import datetime


#%% Get the data
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'

csv_file_covid = datapath + '\\Covid-Data-WI-County.csv'
csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.read_covid_data_wi(csv_file_covid)


#%% Read in currently hospitalized data

# manually downloaded file
hosp_file = "data\\COVID_Patients_(T)_data_2020-09-25.csv"
# url, but it only exists temporarily after I've accessed it manually, not sure how I can get a permalink
hosp_url = "https://bi.wisconsin.gov/vizql/t/DHS/w/EMResourceSnapshotPublic/v/EMResourceSnapshot/vudcsv/sessions/EBB037196DC0415A836E32982F8D0692-3:0/views/12341810530253913541_8071313743224759748?summary=true"

hosp = pd.read_csv(hosp_file)
# discard unnecessary "% change" column
hosp = hosp[['Report Date', 'Region', 'Total COVID Patients']]
# shorten names
hosp = hosp.rename(columns={'Report Date':'Date', 'Total COVID Patients':'Patients'})
# convert to datetime
hosp['Date'] = pd.to_datetime(hosp['Date'])
# pivot
hosp = hosp.pivot(index='Date', columns='Region', values='Patients')
# reorder to the same order as the DHS website
regions = ['Northeast', 'Northwest', 'North Central', 'Fox Valley', 'Southeast', 'Western', 'South Central']
hosp = hosp[regions]

#plot
colors = ['dimgrey', 'teal', 'tab:olive', 'tab:purple', 'olivedrab', 'firebrick', 'tab:blue']
hosp.plot(color=colors)

# plot without southeast
regions2 = ['Northeast', 'Northwest', 'North Central', 'Fox Valley', 'Western', 'South Central']
colors2 = ['dimgrey', 'teal', 'tab:olive', 'tab:purple', 'firebrick', 'tab:blue']
# hosp[regions2].plot(color=colors2)

# create grid of plots


fig, axs = plt.subplots(nrows=2, ncols=3, sharex=True, sharey=True, constrained_layout=True)

for rr, region in enumerate(regions2):
    # divide by plotting scale factor  
    hosp[region].plot(ax=axs.flat[rr], color=colors2[rr], legend=None)
    axs.flat[rr].set_title(region)
    
# y labels
axs[0,0].set_ylabel('Patients')
axs[1,0].set_ylabel('Patients')
plt.suptitle('Patients Hospitalized by Region')

#%% Hospitalization by county

counties = ['WI', 'Milwaukee', 'Brown', 'Dane']
county = 'Brown'

select = covid.select_data(widata, county, ['HOSP_YES'])

select['New Hospitalizations'] = select['HOSP_YES'].diff()

select.plot(y = 'New Hospitalizations')



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





