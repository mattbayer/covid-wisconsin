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
import plotly.express as px
import json



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
plotpath = '.\\docs\\assets\\plotly'

regiondata['NAME'] = regiondata['Region']
region_ordered = ['Northwest', 'North Central', 'Northeast', 
                  'Western',   'Fox Valley',    'Southeast',
                  'South Central', 'Madison', 'Milwaukee']
# color_dict = {'Northwest':     'teal',
#               'North Central': 'darkkhaki',
#               'Northeast':     'dimgrey',
#               'Western':       'firebrick',
#               'Fox Valley':    'mediumpurple',
#               'Outer Southeast': 'olivedrab',
#               'Outer South Central': 'steelblue',
#               'Madison':       'blue',
#               'Milwaukee':     'green'}

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

#%% Facet plot
# covid.plotDCT(regiondata, region_ordered, per_capita=True, popdata=pop_region)

covid.plotly_casetest(sourcedata=capita[capita.Date >= datetime.datetime(year=2020, month=7, day=1)],  
                      case_col='Cases', 
                      test_col='Tests', 
                      date_col='Date',
                      groupby='Region',
                      grouplist=region_ordered, 
                      groupcolors=colors,
                      savefile=plotpath + '\\Cases-Tests-Region.html',
                      plotlabels=dict(title='Regional Cases and New People Tested<br>(per 100K population)',
                                      yaxis='Cases per 100K',
                                      yaxis_secondary='Tested per 100K',
                                      ),
                      )


#%% Hospitalizations
# Individual county data has a big spike when they first started recording 
# hospitalizations.  For now, just filter on dates after the summer.

covid.plotly_deadhosp(sourcedata=capita[capita.Date >= datetime.datetime(year=2020, month=7, day=1)], 
                      dead_col='Deaths', 
                      hosp_col='Hospitalizations', 
                      date_col='Date',
                      groupby='Region',
                      grouplist=region_ordered, 
                      groupcolors=colors,
                      savefile=plotpath + '\\Deaths-Hosp-Region.html',
                      plotlabels=dict(title='Regional Deaths and Hospitalizations<br>(per 100K population)',
                                      yaxis='Deaths and Hosp per 100K',
                                      ),
                      )

# # Deaths / Hospitalizations - example of using twolines explicitly
# covid.plotly_twolines(sourcedata=capita[capita.Date >= datetime.datetime(year=2020, month=7, day=1)],
#                       column1='Deaths',
#                       column2='Hospitalizations',
#                       date_col='Date',
#                       groupby='Region',
#                       grouplist=region_ordered,
#                       groupcolors=colors,
#                       savefile=plotpath + '\\Deaths-Hosp-Region-temp.html',
#                       plotcolors=['firebrick', 'darkorange', 'rosybrown'],
#                       plotlabels=dict(title='Regional Deaths and Hospitalizations per 100K',
#                                       yaxis='Per 100K',
#                                       ),
#                       )

#%% Create map of regions

if False:
    from plotly.offline import plot as pplot
    
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
    # base = countiesWI.plot(column='Region', color=colors, edgecolor='w', linewidth=0.5)
    
    
    # filter counties shapefile to WI, convert to JSON format string, then decode 
    # to dictionary with json.loads()
    countiesJS = json.loads(countiesWI.to_json())
    
    fig = px.choropleth(countiesWI, 
                        geojson=countiesJS, 
                        locations=countiesWI.index, 
                        color='Region', 
                        color_discrete_map=color_dict,
                        category_orders={'Region': list(color_dict.keys())},
                        title='WI Regions',
                        projection='mercator')
    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_traces(marker_line_color='white')
    
    pplot(fig, 
          filename=plotpath+'\\Map-Region.html',
          include_plotlyjs='cdn',
          )
