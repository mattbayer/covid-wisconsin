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

update = True

#%% Auto-download the google file
if update:
    
    import zipfile
    import requests
    
    zip_url = 'https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip'
    mobility_dir = '.\\data\\mobility\\'
    
    # download the zip file
    r = requests.get(zip_url)
    # write the zip file
    zip_filename = os.path.join(mobility_dir, 'Google_Region_Mobility_Report_CSVs.zip')
    open(zip_filename, 'wb').write(r.content)
    
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extract('2020_US_Region_Mobility_Report.csv', path=mobility_dir)
        
    # remove temp zip file
    os.remove(zip_filename)

#%%
apple_file = '.\\data\\mobility\\applemobilitytrends-2020-11-08.csv'
google_file = '.\\data\\mobility\\2020_US_Region_Mobility_Report.csv'

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

#%% Plot categories for a single county or the state
google_state = google_wi[google_wi['iso_3166_2_code'] == 'US-WI']
google_state = google_state.set_index('Date')
google_state = google_state[data_cols]
google_state.plot()

county = 'Dane'
google_county = google_wi[google_wi['County'] == (county+' County')]
google_county = google_county.set_index('Date')
google_county = google_county[data_cols]

google_county.plot()

#%% Or compare counties

counties = ['Milwaukee County', 'Dane County', 'Brown County']
# counties = ['Brown County', 'Outagamie County', 'Winnebago County']
category = 'Retail/Recreation'
# category = 'Workplace'
# category = ['Workplace', 'Retail/Recreation']

google_category = google_wi.pivot(index='Date', columns='County', values=category)

google_category = google_category[counties]

google_category.plot(title=category)

#%% Plotly versions
import plotly.express as px
from plotly.offline import plot as pplot

# don't show transit
data_cols = ['Retail/Recreation', 'Workplace', 'Parks', 'Residential', 'Grocery/Pharmacy']
google_state.columns.name='Category'

# State
fig = px.line(
    google_state, 
    x=google_state.index, 
    y=data_cols,
    title='Wisconsin Google Mobility',
    range_y=[-90, 200],
    )
fig.update_layout(legend_title_text='Category')

pplot(
      fig, 
      filename='.\\docs\\assets\\plotly\\Mobility-Google-WI.html',
      include_plotlyjs='cdn',
      )
fig.write_image(
    '.\\docs\\assets\\Mobility-Google-WI.png',
    width=700,
    height=600,
    engine='kaleido',
    )



#%% Comparison
category = ['Workplace', 'Retail/Recreation']
counties = ['Milwaukee County', 'Dane County', 'Brown County']
# take out whole-state
google_compare = google_wi[google_wi['iso_3166_2_code'] != 'US-WI']
# sort to the chosen categories and counties
google_compare = google_compare.pivot(index='Date', columns='County', values=category)
google_compare = google_compare.swaplevel(axis=1)
google_compare = google_compare[counties]
google_compare.columns.names = ['County', 'Category']
google_compare = google_compare.reset_index()
google_compare = google_compare.melt(id_vars='Date', value_name='Mobility (%)')

fig = px.line(
    google_compare, 
    x='Date',
    y='Mobility (%)', 
    color='County',
    facet_col='Category',
    facet_col_wrap=1,
    # color_discrete_sequence=['#636EFA', '#EF553B', 'saddlebrown'],
    title='Workplace and Retail/Recreation by County',
    )
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font_size=14))

pplot(
      fig, 
      filename='.\\docs\\assets\\plotly\\Mobility-Google-3county.html',
      include_plotlyjs='cdn',
      )

fig.write_image(
    '.\\docs\\assets\\Mobility-Google-3county.png',
    width=700,
    height=600,
    engine='kaleido',
    )

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

apple_county.plot(title='Apple data, '+county+' County')

#%% Compare counties for a single type
transp = 'walking'

apple_type = apple_counties[apple_counties['transportation_type'] == transp]
apple_type = apple_type.pivot(index='Date', columns='region', values='value')
apple_type = apple_type[counties]

apple_type.plot(title=transp)
