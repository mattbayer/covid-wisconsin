# -*- coding: utf-8 -*-
"""
Update plots for regional cases/tests and deaths/hospitalizations.
"""

import pandas as pd
import datetime
import os

import covid

#%% Cases per 100K max for y-axes
per100k = 80

#%% Get the data


# population data
csv_file_pop = '.\\data\\Population-Data-WI.csv'
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.download_covid_data_wi('county2')
# widata = covid.read_covid_data_wi('county')


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
widata['Region'] = widata.GEOName.apply(lambda n: region_map[n])

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
              'POS_NEW_CONF': 'Cases',      # confirmed cases
              'TESTS_NEW': 'Tests',         # total tests
              'DTH_CONF_Daily': 'Deaths',   # by date of death
              }

regiondata = regiondata[col_rename.keys()]
regiondata = regiondata.rename(columns=col_rename)

# convert to date and discard the time portion
regiondata.Date = pd.to_datetime(regiondata.Date).apply(lambda d: d.date())
regiondata = regiondata.sort_values('Date')


#%% compute percent positive - NEED TO GROUP BY REGION
regiondata['Percent positive'] = regiondata['Cases'] / regiondata['Tests']

# compute 7-day averages inside region groups
regiondata['Cases (7-day)'] = regiondata.groupby('Region').Cases.rolling(7).mean().reset_index(level=0, drop=True)
regiondata['Tests (7-day)'] = regiondata.groupby('Region').Tests.rolling(7).mean().reset_index(level=0, drop=True) 
regiondata['Percent positive (7-day avg)'] = regiondata['Cases (7-day)'] / regiondata['Tests (7-day)']


#%% convert per-capita (per 100K)
regiondata['RegionPop'] = regiondata.Region.apply(lambda n: pop_region[n])
capita = regiondata.copy()
datacols = ['Cases', 'Tests', 'Deaths', 'Cases (7-day)', 'Tests (7-day)']
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
              'Milwaukee':     'navy',
              '': 'black'}

colors = [color_dict[r] for r in region_ordered]


#%% Grid plot - Cases / % Positive
plotpath = '.\\docs\\_includes\\plotly'
savefile = plotpath+'\\Cases-Positivity-Region.html'

region_ordered2 = ['Northwest', '',
                   'North Central',  'Northeast',  
                   'Western', 'Fox Valley',
                   'South Central', 'Southeast',
                   'Madison', 'Milwaukee']
colors2 = [color_dict[r] for r in region_ordered2]


fig = covid.plotly_twolines(
    capita, 
    'Cases', 
    'Percent positive (7-day avg)',
    groupby='Region',
    grouplist=region_ordered2,
    groupcolors=colors2,
    ncol=2,
    plotcolors=['steelblue', 'darkmagenta', 'lightsteelblue'],
    secondary_scale=1/400,
    date_min=datetime.datetime(2021,1,15),
    range_max=per100k,
    col1_mode='avg-bar',
    col2_mode='line',
    plotlabels = {'title': 'Regional Cases and Percent Positive',
                  'yaxis': 'Cases per 100K',
                  'yaxis_secondary': 'Percent positive',
                  },
    savefile=savefile,
    showfig=False,
    )

# fig.update_xaxes(title_text='Date of test result')
fig.update_yaxes(secondary_y=True, tickformat=',.0%')
fig.update_traces(secondary_y=True, hovertemplate='%{y:.1%}')

# add image of regions
fig.add_layout_image(
    dict(
        source='https://covid-wisconsin.com/assets/Map-Regions-Small.png',
        xref="paper", yref="paper",
        x=1, y=0.95,
        sizex=0.28, sizey=0.28,
        xanchor='right', yanchor='middle'
    )
)

# Insert breaks into trace names for legend
fig.update_traces(name='Percent positive<br>(7-day avg)',
                  selector=dict(name='Percent positive (7-day avg)'))
fig.update_traces(name='Cases<br>(7-day avg)',
                  selector=dict(name='Cases (7-day avg)'))

# move legend
fig.update_layout(
    legend=dict(
        orientation='v',
        yanchor="top", 
        y=1, 
        xanchor="left", 
        x=0.48,
        font_size=13,
        bgcolor='rgba(0,0,0,0)',
    )
)     


fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    default_height=1000,
    )      
os.startfile(savefile)

