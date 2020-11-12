# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 16:00:54 2020

@author: matt_
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

import covid

#%%
apple_file = '.\\data\\mobility\\applemobilitytrends-2020-11-08.csv'
google_file = '.\\data\\mobility\\2020_US_Region_Mobility_Report-2020-11-08.csv'

apple_csv = pd.read_csv(apple_file)
google_csv = pd.read_csv(google_file)

#%% Google processing

col_rename = {'retail_and_recreation_percent_change_from_baseline': 'Retail/Recreation',
              'grocery_and_pharmacy_percent_change_from_baseline': 'Grocery/Pharmacy',
              'parks_percent_change_from_baseline': 'Parks',
              'transit_stations_percent_change_from_baseline': 'Transit',
              'workplaces_percent_change_from_baseline': 'Workplace',
              'residential_percent_change_from_baseline': 'Residential',
              'sub_region_2': 'County',
              'date': 'Date'}

data_cols = ['Retail/Recreation', 'Grocery/Pharmacy', 'Parks', 'Transit', 'Workplace', 'Residential']

google_wi = google_csv[google_csv['sub_region_1'] == 'Wisconsin']
google_wi = google_wi.rename(columns=col_rename)

#%% Plot categories for a single county
county = 'Dane'
google_county = google_wi[google_wi['County'] == (county+' County')]
google_county = google_county.set_index('Date')
google_county = google_county[data_cols]

google_county.plot()

#%% Or compare counties

counties = ['Milwaukee County', 'Dane County', 'Brown County']
# category = 'Retail/Recreation'
category = 'Workplace'

google_wi = google_wi
google_category = google_wi.pivot(index='Date', columns='County', values=category)

google_category = google_category[counties]

google_category.plot(title=category)


#%% Apple processing

apple_wi = apple_csv[apple_csv['sub-region']=='Wisconsin']
# isolate counties - there are also cities and the state as a whole
apple_counties = apple_wi[apple_wi['geo_type']=='county']
# take out redundant columns
cols = list(apple_counties.columns);
cols.remove('geo_type')
cols.remove('alternative_name')
cols.remove('sub-region')
cols.remove('country')
apple_counties = apple_counties[cols]
# melt date columns into a single column
apple_counties = apple_counties.melt(id_vars=['region', 'transportation_type'], var_name='Date')
# convert to real date format
apple_counties.Date = pd.to_datetime(apple_counties.Date)



#%% Compare types for a single county
county = 'Dane'
apple_county = apple_counties[apple_counties['region'] == county+' County']
apple_county = apple_county.pivot(index='Date', columns='transportation_type', values='value')

apple_county.plot(title=county+' County')

#%% Compare counties for a single type
transp = 'walking'

apple_type = apple_counties[apple_counties['transportation_type'] == transp]
apple_type = apple_type.pivot(index='Date', columns='region', values='value')
apple_type = apple_type[counties]

apple_type.plot(title=transp)
