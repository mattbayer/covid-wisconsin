# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 15:36:02 2022

@author: 212367548
"""

import pandas as pd
import numpy as np
import datetime
import os

import covid

# Data from 
# https://data.cdc.gov/Case-Surveillance/United-States-COVID-19-Cases-and-Deaths-by-State-o/9mfq-cb36
fname = 'United_States_COVID-19_Cases_and_Deaths_by_State_over_Time.csv'

#%% 
# Move file from downloads to storage folder
os.replace(os.path.join('C:\\Users\\212367548\\Downloads', fname), os.path.join('data', fname))
# os.replace(os.path.join('C:\\Users\\matt_\\Downloads', fname), os.path.join('data', fname))

#%% Read and process data

cases_full = pd.read_csv(os.path.join('data', fname))
cases_full.submission_date = pd.to_datetime(cases_full.submission_date)

col_list = ['submission_date', 'state', 
            'tot_cases', 'conf_cases', 'prob_cases',
            'new_case', 'pnew_case',
            ]
            # 'created_at']

cases_full = cases_full[col_list]
cases_full = cases_full.sort_values('submission_date')

cases = cases_full.groupby('submission_date').sum()
# cases_full[cases_full.state=='NYC'].sort_values('submission_date').tail(14)

cases['new_case_7'] = cases.new_case.rolling(7).mean()

cases = cases[cases.index >= pd.to_datetime('2022-01-15')]

cases['projection1'] = 1e5 * np.exp(-0.079*(cases.index.copy() - pd.to_datetime('2022-02-19')).days)
t2 = (cases.index.copy() - pd.to_datetime('2022-02-21')).days
cases['projection2'] = 85e3 * np.exp(-0.052 * t2)
t3 = (cases.index.copy() - pd.to_datetime('2022-02-14')).days
cases['projection3'] = 145e3 * np.exp((-0.075 + 0.0008*t3) * t3 )




#%% Model of BA2 (from Matlab originally)

x = np.arange(0,14);    # week; 0 = Feb 6
offset = 5.5;
# ba1_factor = 0.6;
# ba1_factor - gradually increasing factor of decrease
# ba1_factor = 0.59 + 0.01*x
ba1_factor = 0.57 + 0.000*x
ba1_factor_cum = np.insert(ba1_factor.cumprod(), 0, 1)[0:-1]

ba2_exp = 0.8;     # exponential coeff to match observed increase in share
ba2_factor = np.exp(ba2_exp) * ba1_factor;     # convert to factor for increase in number

ba2 = 1 / (1+np.exp(-ba2_exp*(x-offset)))
ba1 = 1 - ba2;

start = 280;    # thousand cases

C = np.zeros((len(x), 3));
C[:,0] = start * ba1[0] * ba1_factor_cum;
C[:,1] = start * ba2[0] * ba2_factor**x;

C[:,2] = C.sum(axis=1);

print(C)

# figure
# semilogy(cases)

t4 = ((cases.index.copy() - pd.to_datetime('2022-03-20')).days)/7 + 6
cases['ba2'] = np.interp(t4, x, C[:,2]) * 1e3

#%% Plot and print

cases.plot(y=['new_case_7', 'projection2', 'projection3', 'ba2'], logy=True)

print(cases.iloc[-15:,[3,5,8,9]])
