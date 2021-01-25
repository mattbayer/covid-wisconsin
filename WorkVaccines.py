# -*- coding: utf-8 -*-
"""
Update plots for regional vaccine allocation
"""

import pandas as pd
import datetime

import covid

#%% Get the data
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'

csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.read_covid_data_wi('county')


#%% Sum up population by region

# get mapping between county and region
region_file = 'data\\Regions-WI.csv'

region_map = pd.read_csv(region_file)
region_map = region_map[['County',  'Modified HERC Short']]
region_map = region_map.set_index('County')
region_map = region_map.squeeze()

# get a list of region names
region_list = region_map.unique()

# add WI overall to the map
region_map['WI'] = 'WI'

# apply this map to the county name column to create a new Region column
widata['Region'] = widata.NAME.apply(lambda n: region_map[n])

# group data by regions
regiondata = widata.groupby(['Date', 'Region']).sum()
regiondata = regiondata.reset_index()

# find population of these regions
popdata_region = popdata.to_frame(name='Population')
popdata_region['Region'] = region_map

pop_region = popdata_region.groupby('Region').sum().squeeze()

#%% Trim data
col_rename = {'Date': 'Date', 
              'Region': 'Region', 
              'POS_NEW': 'Cases',
              'TEST_NEW': 'Tests',
              'DTH_NEW': 'Deaths',
              'HOSP_NEW': 'Hospitalizations',
              }

regiondata = regiondata[col_rename.keys()]
regiondata = regiondata.rename(columns=col_rename)


#%% convert per-capita (per 100K)
regiondata['RegionPop'] = regiondata.Region.apply(lambda n: pop_region[n])
capita = regiondata.copy()
datacols = ['Cases', 'Tests', 'Deaths', 'Hospitalizations']
capita[datacols] = regiondata[datacols].div(regiondata['RegionPop'], axis=0) * 100000


#%% Region names and colors
plotpath = '.\\docs\\_includes\\plotly'

regiondata['NAME'] = regiondata['Region']
region_ordered = ['Northwest', 'North Central', 'Northeast', 
                  'Western',   'Fox Valley',    'Southeast',
                  'South Central', 'Madison', 'Milwaukee']

color_dict = {'Northwest':     'thistle',
              'North Central': 'khaki',
              'Northeast':     'green',
              'Western':       'sandybrown',
              'Fox Valley':    'yellowgreen',
              'Southeast': 'lightsteelblue',
              'South Central': 'pink',
              'Madison':       'red',
              'Milwaukee':     'navy'}

colors = [color_dict[r] for r in region_ordered]



#%% Vaccine numbers
# 25-Jan
vaccine_region =    {'Northwest': 28443, 
                      'North Central': 25285, 
                      'Northeast': 30578,
                      'Western': 17984,   
                      'Fox Valley':23719,    
                      'Southeast':116672,
                      'South Central':89329, 
                      'Madison': 49644, 
                      'Milwaukee': 46190,
                      'WI': 339858
                     }

# dis-aggregate Milwaukee and Madison
vaccine_region['Southeast'] = vaccine_region['Southeast'] - vaccine_region['Milwaukee']
vaccine_region['South Central'] = vaccine_region['South Central'] - vaccine_region['Madison']

vaccine_region = pd.Series(vaccine_region)

# per-capita vaccinations

vaccine_capita = vaccine_region / pop_region