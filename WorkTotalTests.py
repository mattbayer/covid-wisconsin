# -*- coding: utf-8 -*-
"""
Trying to predict total tests from persons tested

Created on Wed Dec  2 09:19:48 2020

@author: 212367548
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import covid
import urllib
from scipy import signal
import datetime
import os

#%% By Test vs. people tested


# manually downloaded file - positives and tests
test_file = "data\\By_Test_Data_data_2020-12-02.csv"


# Load file and rearrange some stuff
test = covid.read_bytest_wi(test_file)
test = test.set_index('Date')
test = test.rename(columns={'Tests': 'New tests'})

# cumulative sum of tests
test['Total tests'] = test['New tests'].expanding(1).sum()



#%% By People
# cases and new people tested
people_file = "data\\By_Person_Data_data_2020-12-02.csv"
people = pd.read_csv(people_file)

# this file has lots of duplicates for some reason, but you can filter on one 
# of the columns 
# people = people[people['Measure Names']=='People tested positive']
people = people[~pd.isna(people['Max. Result Date'])]

col_rename = {'Day of Result Date': 'Date', 'Positive.y': 'Cases', 'Total.Y': 'New people tested' }

people = people[col_rename.keys()]
people = people.rename(columns=col_rename)
people['Date'] = pd.to_datetime(people['Date'])
people = people.set_index('Date')

people['Cases'] = pd.to_numeric(people['Cases'].str.replace(',',''))
people['New people tested'] = pd.to_numeric(people['New people tested'].str.replace(',',''))


test['New people tested'] = people['New people tested']
# cumulative sum of tests
test['Total people tested'] = test['New people tested'].expanding(1).sum()

# people.plot(y=['Cases', 'New people tested'])

#%% By Report

state = covid.read_covid_data_wi('state')
state = state.set_index('Date')
state['Tested'] = state['POSITIVE'] + state['NEGATIVE']

test['Total people tested (reported)'] = state['Tested']
test['New people tested (reported)'] = test['Total people tested (reported)'].diff(1)

# compare cases test date to reported date
people['Cases (reported)'] = state['POS_NEW']
people.rolling(7).mean().plot(y=['Cases', 'Cases (reported)'])
# CAREFUL- I thought it was by TEST date, 
# but I think it's actually by RESULT date. 
# The plots LOOK not all that different, but that might be an artifact of just
# having very similar 7-day patterns. If I average it maybe I would see more
# of a delay like I would expect.
# If I do the average, then it looks like something like a 5 day delay.
# Still not clear to me if that's only between test result and report, or 
# test date and report.

#%% Plot tests and people
test.plot(y=['New tests', 'New people tested', 'New people tested (reported)'])
test.plot(y=['Total tests', 'Total people tested', 'Total people tested (reported)'])

#%% Derived ratio of tests and people

Npop = 5.8e6
test['Tests/People'] = test['Total tests'] / test['Total people tested']
test['New Tests/People'] = test['New tests'] / test['New people tested']
test['Fraction tested'] = test['Total people tested'] / Npop

c = 1.15
k = 3.3
test['Model ratio 1'] = 1 / (1 - test['Fraction tested'])
test['Model ratio 2'] = c + k*test['Fraction tested']

test['Tests model'] = test['New people tested'] * (c + k*test['Fraction tested'])

test.plot(y=['Tests/People', 'New Tests/People', 'Model ratio 1', 'Model ratio 2'])
test.plot(x='Fraction tested', y=['New Tests/People', 'Model ratio 1', 'Model ratio 2'])

# weird - total tested from the by-date plot is lower overall than the total 
# tested from the reporting totals. I don't think I made any mistakes, I checked
# that I'm including positives.
# Ooh, maybe it's this from DHS:
    # If they tested positive more than once, they are only included once on the date of their first positive test result. People who tested negative and never positive (gray bars) are counted once on the date of their first negative test result. However, if someone tests negative, then positive at a later date, they are removed from the negative count and are now counted as a positive.
# So could it be the by-date plot removes first negatives if later they're positive, but the reported one doesn't?
# I also noticed older data was higher in old dates, so that would make sense of that.

#%% Use model to predict Milwaukee

county = covid.read_covid_data_wi('county')
mke = county[county.NAME=='Milwaukee']
mke = mke.set_index('Date')
mke['Total tested'] = mke.POSITIVE + mke.NEGATIVE
mke['Fraction tested'] = mke['Total tested'] / 9.46e5
mke = mke.rename(columns={'TEST_NEW': 'New tested'})
mke['Tests model'] = mke['New tested'] * (c + k*mke['Fraction tested'])

mke.plot(y=['New tested', 'Tests model'])

# ends up overestimating total tests by 10%.  Not too bad.
# and remember this is tests by report date, which I've already seen are 
# higher than tests by test date...