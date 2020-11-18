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
import json
import plotly.express as px
from plotly.offline import plot as pplot
import plotly.graph_objects as go

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

#%% Create background to figures

# line_colors = {'land':'darkgrey', 'border':'lightgray', 'marker':'dimgray'}
# line_colors = {'land':'darkgrey', 'border':'dimgray', 'marker':'lightgray'}
# line_colors = {'land':'lightgray', 'border':'white', 'marker':'dimgray'}
line_colors = {'land':'lightgray', 'border':'darkgray', 'marker':'dimgray'}

# background map of counties
fig_bkgd = px.choropleth(countiesWI, 
                         geojson=countiesJS, 
                         locations=countiesWI.index, 
                         color_discrete_sequence=[line_colors['land']],
                         width=600,
                         height=600,
                         projection='mercator')

# turn off hover tooltips for this layer - have to set both of these because
# hovertemplate is set automatically and it supersedes hoverinfo.
# Also take out legend because it's not very useful right now; I could add
# a fancier custom legend later.
fig_bkgd.update_traces(hovertemplate=None, 
                       hoverinfo='skip', 
                       marker_line_color=line_colors['border'],
                       showlegend=False)




#%% Complete the figures - cases
plotcol = 'Cases per 100K'

# copy background
fig_cases = go.Figure(fig_bkgd)
fig_cases.update_layout(title='Cases by County<br>(7-day avg)')

fig_cases.add_trace(go.Scattergeo(lon=countiesWI.plotlon,
                                  lat=countiesWI.plotlat,
                                  text=display_names,
                                  customdata=countiesWI.Population,
                                  marker=dict(size=countiesWI.Cases, #size=countiesWI.Population / popscale,
                                              sizeref=casescale,
                                              color=countiesWI[plotcol],
                                              cmin=case_scale[0],
                                              cmax=case_scale[1],
                                              sizemode='area',
                                              colorscale='Blues'),
                                  line=dict(color=line_colors['marker']),
                                  hovertemplate=
                                  '<b>%{text}</b><br>' +
                                  'Population: %{customdata:.0f}<br>' +
                                  'Cases: %{marker.size:.1f}<br>' + 
                                  'Cases per 100K : %{marker.color:.1f}'+
                                  '<extra></extra>'
                                  ))

# only display wisconsin counties, not whole world
fig_cases.update_geos(fitbounds='locations', visible=False)

pplot(fig_cases, 
      filename='.\\docs\\assets\\plotly\\Map-Cases-WI-1.html',
      include_plotlyjs='cdn')


#%% Hospitalizations
plotcol = 'Hospitalizations per 100K'

# copy background
fig_hosp = go.Figure(fig_bkgd)
fig_hosp.update_layout(title='Hospitalizations by County<br>(7-day avg)')

fig_hosp.add_trace(go.Scattergeo(lon=countiesWI.plotlon,
                                 lat=countiesWI.plotlat,
                                 text=display_names,
                                 customdata=countiesWI.Population,
                                 marker=dict(size=abs(countiesWI.Hospitalizations),
                                             sizeref=hospscale,
                                             color=countiesWI[plotcol],
                                             cmin=hosp_scale[0],
                                             cmax=hosp_scale[1],
                                             sizemode='area',
                                             colorscale='Oranges'),
                                 line=dict(color=line_colors['marker']),
                                 hovertemplate=
                                 '<b>%{text}</b><br>' +
                                 'Population: %{customdata:.0f}<br>' +
                                 'Hospitalizations: %{marker.size:.1f}<br>' + 
                                 'Hospitalizations per 100K: %{marker.color:.1f}' +
                                 '<extra></extra>'
                                 ))

fig_hosp.update_geos(fitbounds='locations', visible=False)

pplot(fig_hosp, 
      filename='.\\docs\\assets\\plotly\\Map-Hosp-WI-1.html',
      include_plotlyjs='cdn')

