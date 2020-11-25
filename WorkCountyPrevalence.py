# -*- coding: utf-8 -*-
"""
Work on county-level prevalence
"""

import geopandas as gpd
import covid

# plotly
import json
import plotly.express as px
from plotly.offline import plot as pplot
import plotly.graph_objects as go

#%% Get the coviddata
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'
csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.read_covid_data_wi('county')


#%% Geography work

# WI DNR shapefile - doesn't have lake winnebago either, so never mind
# shapefile = 'data\\geo\\WI_County_Boundaries_24K.shp'
# countiesWI = gpd.read_file(shapefile)
# countiesWI['NAME'] = countiesWI.COUNTY_NAM

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

# # chloropleth by population from geopandas
# base = countiesWI.plot(column='Population', edgecolor='w', linewidth=0.5)


#%%
latest = widata.loc[widata['Date'] == widata['Date'].max()]
latest = latest.set_index('NAME')
countiesWI['People Tested'] = latest['POSITIVE'] + latest['NEGATIVE']

#%%

quit()

# create new hospitalizations column; need to sort by date first
widata = widata.sort_values('Date')
widata = widata.assign(HOSP_NEW = widata.groupby('NAME').HOSP_YES.diff(periods=1))

# reduce and rename columns
col_rename = {'Date': 'Date', 'NAME': 'County', 'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
reduced = widata[col_rename.keys()]
reduced = reduced.rename(columns=col_rename)

# 7-day rolling average
# reset_index() at end to take result back to original format, instead of counties as a MultiIndex
# reduced_avg = reduced.groupby('County').rolling(window=7, on='Date', center=False).mean().reset_index(level=0)
# last_avg = reduced_avg[reduced_avg.Date == reduced_avg.Date.max()]
# not working...something wrong here.

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

countiesWI['Hospitalizations'] = hosp_for_map
countiesWI['Hospitalizations per 100K'] = countiesWI['Hospitalizations'] / countiesWI['Population'] * 100000



#%% Plotly


do_choropleth = False

plotcol = 'Cases per 100K'
plotcol2 = 'Hospitalizations per 100K'
hosp_scale = [0, 4]

# filter counties shapefile to WI, convert to JSON format string, then decode 
# to dictionary with json.loads()
countiesJS = json.loads(countiesWI.to_json())

#%% Choropleth maps
if do_choropleth:
    fig = px.choropleth(countiesWI, 
                        geojson=countiesJS, 
                        locations=countiesWI.index, 
                        color=plotcol, 
                        color_continuous_scale=px.colors.sequential.Blues,
                        title='Cases by County',
                        projection='mercator')
    fig.update_geos(fitbounds='locations', visible=False)
    
    pplot(fig, filename='.\\plots\\plotly\\temp.html' )
    
    fig2 = px.choropleth(countiesWI, 
                        geojson=countiesJS, 
                        locations=countiesWI.index, 
                        color=plotcol2, 
                        color_continuous_scale=px.colors.sequential.Oranges,
                        range_color=hosp_scale,
                        title='Hospitalizations by County',
                        projection='mercator')
    fig2.update_geos(fitbounds='locations', visible=False)
    
    
    pplot(fig2, filename='.\\plots\\plotly\\temp2.html' )


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
casescale = 0.3
cases_size_factor = casescale
hospscale = casescale*.05   # so that bubbles are same size if hosp = 5% of cases
hosp_scale = [0, 7]
case_scale = [0, 140]
cases_color_range = case_scale

hosp_size_factor=hospscale
hosp_color_range=hosp_scale

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


