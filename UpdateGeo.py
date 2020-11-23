# -*- coding: utf-8 -*-
"""
Create interactive maps for cases and hospitalizations using Plotly.
"""

import geopandas as gpd

import covid

#%% Get the coviddata
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'
csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.read_covid_data_wi('county')


#%% Geography work

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
# add Population column
countiesWI['Population'] = popdata


#%%

# create new hospitalizations column; need to sort by date first
widata = widata.sort_values('Date')
widata = widata.assign(HOSP_NEW = widata.groupby('NAME').HOSP_YES.diff(periods=1))

# reduce and rename columns
col_rename = {'Date': 'Date', 'NAME': 'County', 'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
reduced = widata[col_rename.keys()]
reduced = reduced.rename(columns=col_rename)

avg_window = 7

# isolate cases
cases = reduced.pivot(index='Date', columns='County', values='Cases')
cases_avg = cases.rolling(window=avg_window, center=False).mean()
cases_for_map = cases_avg.iloc[-1]

countiesWI['Cases'] = cases_for_map
countiesWI['Cases per 100K'] = countiesWI['Cases'] / countiesWI['Population'] * 100000

# hospitalizations
hosp = reduced.pivot(index='Date', columns='County', values='Hospitalizations')
hosp_avg = hosp.rolling(window=avg_window, center=False).mean()
hosp_for_map = hosp_avg.iloc[-1]

# set any negative values to 0
def zeroneg(x):
    if x > 0:
        return x
    else:
        return 0
    
hosp_for_map = hosp_for_map.apply(zeroneg)

countiesWI['Hospitalizations'] = hosp_for_map
countiesWI['Hospitalizations per 100K'] = countiesWI['Hospitalizations'] / countiesWI['Population'] * 100000



#%% Bubble map - size is numbers, color is per-population

# get latitude and longitude of centroids of counties for plotting
# this will give warning but I don't care
countiesWI['plotlon'] = countiesWI.geometry.centroid.x
countiesWI['plotlat'] = countiesWI.geometry.centroid.y
# move Milwaukee's plot center to the right a bit to make more room for its bubble
countiesWI.loc['Milwaukee', 'plotlon'] = countiesWI.loc['Milwaukee', 'plotlon'] + 0.15

# append 'County' for display names
display_names = [n + ' County' for n in countiesWI.index]

# set scales for sizes of bubbles
popscale = 300

cases_size_factor = 0.3
hosp_size_factor = cases_size_factor*.05   # so that bubbles are same size if hosp = 5% of cases 

cases_color_range = [0, 140]
hosp_color_range=[0, 7]

#%% Cases figure
covid.plotly_colorbubble(
    countiesWI,
    sizecol='Cases',
    colorcol='Cases per 100K',
    size_factor=cases_size_factor,
    color_range=cases_color_range,
    colorscale='Blues',
    location_names=display_names,
    plotlabels=dict(title='Cases by County<br>(Daily, 7-day avg)'),
    savefile='.\\docs\\assets\\plotly\\Map-Cases-WI.html',
    fig_height=600,
    )

#%% Hospitalizations figure
covid.plotly_colorbubble(
    countiesWI,
    sizecol='Hospitalizations',
    colorcol='Hospitalizations per 100K',
    size_factor=hosp_size_factor,
    color_range=hosp_color_range,
    colorscale='Oranges',
    location_names=display_names,
    plotlabels=dict(
        title='Hospitalizations by County<br>(Daily, 7-day avg)',
        colorlabel='Hosp per 100K',
        ),
    savefile='.\\docs\\assets\\plotly\\Map-Hosp-WI.html',
    fig_height=600,
    )


