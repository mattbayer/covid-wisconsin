# -*- coding: utf-8 -*-
"""
Work on positivity rate

Comparing positivity rate for new persons, vs. all tests
"""
# path = 'C:/dev/Covid/'
path = './'

import numpy as np
import pandas as pd
import geopandas as gpd
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
widata = covid.read_covid_data_wi('county')



#%% Sum up population by region

# get mapping between county and region
region_file = 'data\\Regions-WI.csv'

region_map = pd.read_csv(region_file)
region_map = region_map[['County',  'Modified HERC']]
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

#%% Facet plot
regiondata['NAME'] = regiondata['Region']
region_ordered = ['Northwest', 'North Central', 'Northeast', 
                  'Western',   'Fox Valley',    'Outer Southeast',
                  'Outer South Central', 'Madison', 'Milwaukee']
covid.plotDCT(regiondata, region_ordered, per_capita=True, popdata=pop_region)


#%% Create map of regions

# shapefile from US census - doesn't have lake winnebago which is annoying
shapefile = 'data\\geo\\cb_2019_us_county_500k.shp'
# read data set of all USA counties
countiesUSA = gpd.read_file(shapefile)
# filter on wisconsin
countiesWI = countiesUSA[countiesUSA.STATEFP == '55']

# reindex on county name
countiesWI = countiesWI.set_index('NAME')
# sort by name
countiesWI = countiesWI.sort_index()
# add Region column
countiesWI['Region'] = region_map

# chloropleth by population from geopandas
base = countiesWI.plot(column='Region', edgecolor='w', linewidth=0.5)

