# -*- coding: utf-8 -*-
"""
Work on people tested gap 10-17

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


#%% By People
# cases and new people tested


def load_people_file(people_file):
    people = pd.read_csv(people_file)   
    people = people[people['Measure Names']=='People tested positive']   
    col_rename = {'Day of Result Date': 'Date', 'Positive.y': 'Cases', 'Total.Y': 'New people tested' }   
    people = people[col_rename.keys()]
    people = people.rename(columns=col_rename)
    people['Date'] = pd.to_datetime(people['Date'])
    people = people.set_index('Date')
    return people

people1 = load_people_file("data\\By_Person_Data_data_2020-10-19B.csv")
people = load_people_file("data\\By_Person_Data_data_2020-10-20.csv")

people['Tested Oct-20'] = people['New people tested']
people['Tested Oct-18'] = people1['New people tested']

people['Tested Oct-18'] = people['Tested Oct-18'].fillna(0)

difference = people['Tested Oct-20'] - people['Tested Oct-18']
plt.figure()
difference.plot()
print(difference.sum())

#%% By Tests
# manually downloaded file - positives and tests

def load_test_file(test_file):
    test = pd.read_csv(test_file)
    test = test[test['Measure Names']=='Positive tests']
    col_rename = {'Day of displaydateonly': 'Date', 'Positives': 'Positives', 'Totals': 'Tests' }
    test = test[col_rename.keys()]
    test = test.rename(columns=col_rename)
    test['Date'] = pd.to_datetime(test['Date'])
    test = test.set_index('Date')
    return test
    
test1 = load_test_file("data\\By_Test_Data_data_2020-10-19.csv")
test = load_test_file("data\\By_Test_Data_data_2020-10-19B.csv")

test['Tests Oct-19'] = test['Tests']
test['Tests Oct-18'] = test1['Tests']

test['Tests Oct-18'] = test['Tests Oct-18'].fillna(0)

difference = test['Tests Oct-19'] - test['Tests Oct-18']
plt.figure()
difference.plot()
print(difference.sum())