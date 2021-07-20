# -*- coding: utf-8 -*-
"""
Trying to predict total tests from persons tested, for purposes of estimating 
a regional test positivity rate.

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

 
#%% Get positive and total tests
# pos_df = covid.scrape_widash_postest()

test = pos_df
test['New tests'] = test['Tests']
test['Cases'] = test['Positive tests']

test = test.set_index('Date')
test['New tests (7-day)'] = test['New tests'].rolling(7).mean()

# cumulative sum of tests
test['Total tests'] = test['New tests'].expanding(1).sum()




#%% By Report

state = covid.read_covid_data_wi('state')
state = state.set_index('Date')
state['Tested'] = state['POSITIVE'] + state['NEGATIVE']

test['Total people tested (reported)'] = state['Tested']
test['New people tested (reported)'] = test['Total people tested (reported)'].diff(1)
test['New people tested (7-day)'] = test['New people tested (reported)'].rolling(7).mean()


#%% Plot tests and people
test.plot(y=['New tests', 'New people tested (reported)'])
test.plot(y=['New tests (7-day)', 'New people tested (7-day)'])
test.plot(y=['Total tests', 'Total people tested (reported)'])

#%% Derived ratio of tests and people

Npop = 5.8e6
test['Tests/People'] = test['Total tests'] / test['Total people tested (reported)']
test['New Tests/People (7-day)'] = test['New tests (7-day)'] / test['New people tested (7-day)']
test['Fraction tested'] = test['Total people tested (reported)'] / Npop


def model1(x):
    c = 1.18
    k = 1.6
    return c * (1 - x)**(-k)

# test['Model ratio 1'] = c1 * (1 - test['Fraction tested'])**(-k1)
test['Model ratio 1'] = test['Fraction tested'].apply(model1)


def model2(x):
    c = 1.15
    k = 3.3
    return c + k*x


test['Model ratio 2'] = test['Fraction tested'].apply(model2)

test['Total tests model 1'] = (test['New people tested (reported)'] * test['Model ratio 1']).expanding(1).sum()

test.plot(y=['Tests/People', 'New Tests/People (7-day)', 'Model ratio 1', 'Model ratio 2'])
test.plot(x='Fraction tested', y=['New Tests/People (7-day)', 'Model ratio 1', 'Model ratio 2'])
test.plot(y=['Total tests', 'Total tests model 1', 'Total people tested (reported)'])


#%% Use model to predict Milwaukee

county = covid.read_covid_data_wi('county')
mke = county[county.NAME=='Milwaukee']
mke = mke.set_index('Date')
mke['Total tested'] = mke.POSITIVE + mke.NEGATIVE
mke['Fraction tested'] = mke['Total tested'] / 9.46e5
mke = mke.rename(columns={'TEST_NEW': 'New tested'})

mke['Tests model 1'] = mke['New tested'] * mke['Fraction tested'].apply(model1)
mke['Tests model 2'] = mke['New tested'] * mke['Fraction tested'].apply(model2)

mke.plot(y=['New tested', 'Tests model 1', 'Tests model 2'])
