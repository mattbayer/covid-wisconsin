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

# Move file from downloads to storage folder
fname = 'United_States_COVID-19_Cases_and_Deaths_by_State_over_Time.csv'
os.replace(os.path.join('C:\\Users\\212367548\\Downloads', fname), os.path.join('data', fname))


#%% Read and process data

cases_full = pd.read_csv(os.path.join('data', fname))

col_list = ['submission_date', 'state', 
            'tot_cases', 'conf_cases', 'prob_cases',
            'new_case', 'pnew_case',
            ]
            # 'created_at']

cases = cases_full[col_list]
cases.submission_date = pd.to_datetime(cases.submission_date)

cases = cases.groupby('submission_date').sum()
# cases = cases[cases.state=='MA'].set_index('submission_date').sort_index()

cases['new_case_7'] = cases.new_case.rolling(7).mean()

cases = cases[cases.index >= pd.to_datetime('2022-01-15')]

cases['projection1'] = 1e5 * np.exp(-0.079*(cases.index.copy() - pd.to_datetime('2022-02-19')).days)
cases['projection2'] = 85e3 * np.exp(-0.052*(cases.index.copy() - pd.to_datetime('2022-02-21')).days)

cases.plot(y=['new_case_7', 'projection1', 'projection2'], logy=True)

print(cases.iloc[-14:,[3,5,6,7]])
