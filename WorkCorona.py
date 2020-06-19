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


#%% Retrieve data from server and save to csv file

csv_file_covid = path + 'Covid-Data-WI.csv'
csv_file_pop = path + 'Population-Data-WI.csv'

# download population data
# covid.download_pop_data_wi(csv_file_pop)

# comment out if no need to re-download    
# covid.download_covid_data_wi(csv_file_covid)

#%% Read data from the previously saved csv file


widata = covid.read_covid_data_wi(csv_file_covid)

popdata = covid.read_pop_data_wi(csv_file_pop)





#%% Plot cases and deaths for the state

# use seaborn theme for plotting
# sns.set()

covid.plot_tests_posrate(widata, 'WI')
covid.plot_cases_deaths(widata, 'WI')
covid.plot_cases_tests(widata, 'WI')

covid.plot_cases_deaths(widata, 'Milwaukee')
covid.plot_cases_tests(widata, 'Milwaukee')

covid.plot_cases_deaths(widata, 'Brown')
covid.plot_cases_deaths(widata, 'Racine')
covid.plot_cases_tests(widata, 'Racine')

#%%
covid.plot_by_county(widata, popdata, 'DTH_NEW', 6)

#%% 
covid.plot3(widata, 'WI')


