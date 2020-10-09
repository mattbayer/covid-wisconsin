# -*- coding: utf-8 -*-
"""
Work for blog post on true prevalance
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


#%% Get the data
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'

csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.read_covid_data_wi()


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
# add whole state 
hosp['WI'] = hosp.sum(axis=1)

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


#%% Sum up population by region

# get mapping between county and region
region_file = 'data\\HERC-Region-WI.csv'

region_map = pd.read_csv(region_file)
region_map = region_map.set_index('County')
region_map = region_map.squeeze()
region_map['WI'] = 'WI'

# apply this dict to the county name column to create a new Region column
widata['Region'] = widata.NAME.apply(lambda n: region_map[n])

# find population of these regions
popdata_region = popdata.to_frame(name='Population')
popdata_region['Region'] = region_map

pop_region = popdata_region.groupby('Region').sum().squeeze()


# Plot grid per capita
regions = ['Northwest', 'North Central', 'Northeast', 'Western', 'South Central', 'Fox Valley',  'WI', '', 'Southeast']
colors = ['teal', 'tab:olive', 'dimgrey', 'firebrick', 'tab:blue', 'tab:purple', 'black', '', 'olivedrab']
fig, axs = plt.subplots(nrows=3, ncols=3, sharex=True, sharey=True, constrained_layout=True)

for rr, region in enumerate(regions):
    if region != '':
        # divide by plotting scale factor  
        capita = hosp[region] / pop_region[region] * 1e6
        capita.plot(ax=axs.flat[rr], color=colors[rr], legend=None)
        axs.flat[rr].set_title(region)
    else:
        axs.flat[rr].axis('off')
    
# y labels
axs[1,0].set_ylabel('Patients / mil')
plt.suptitle('Patients Hospitalized Per Million by Region')


#%% College region

college_counties = ['Dane', 'La Crosse', 'Eau Claire', 'Grant', 'Dunn', 'Walworth', 'Portage']
packer_counties = list(region_map[region_map=='Northeast'].index) + list(region_map[region_map=='Fox Valley'].index)

pop_college = popdata[college_counties]

# create a "region" with colleges - will overwrite some other regions
region_map_college = region_map
region_map_college[college_counties] = 'Colleges'

widata['County group'] = widata.NAME.apply(lambda n: region_map_college[n])



#%%

hosp_college = widata.groupby(['Date', 'County group']).HOSP_YES.sum()
case_college = widata.groupby(['Date', 'County group']).POSITIVE.sum()

# hosp_region = widata.groupby(['Date', 'Region']).HOSP_YES.sum()
# case_region = widata.groupby(['Date', 'Region']).POSITIVE.sum()

hosp_college = hosp_college.unstack()
case_college = case_college.unstack()

hosp_college['Packerland'] = hosp_college['Northeast'] + hosp_college['Fox Valley']
case_college['Packerland'] = case_college['Northeast'] + case_college['Fox Valley']

hosp_new = hosp_college.diff(periods=7)/7
case_new = case_college.diff(periods=7)/7



# limit the dates
date_start = datetime.datetime(2020, 6, 1)
hosp_new = hosp_new.iloc[hosp_new.index >= date_start]
case_new = case_new.iloc[case_new.index >= date_start]

fig, axs = plt.subplots(nrows=1, ncols=2, constrained_layout=True)

case_new.plot(ax=axs[0], y=['Colleges', 'Packerland'], color=['red', 'darkgreen'], style=['--', '-'], title='Two outbreaks: daily cases (7-day avg)')
hosp_new.plot(ax=axs[1], y=['Colleges', 'Packerland'], color=['red', 'darkgreen'], style=['--', '-'], title='Two outbreaks: daily hospitalizations (7-day avg)')


#%%
quit()

#%% Copy of WorkTruePrevalence
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










