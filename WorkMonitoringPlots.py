# -*- coding: utf-8 -*-
"""
Work on new plots for monitoring the situation.

Created on Wed Jun 30 10:48:03 2021

@author: 212367548
"""

import pandas as pd
import geopandas as gpd
import datetime
from plotly.offline import plot as pplot
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

import covid

from tableauscraper import TableauScraper as TS
ts = TS()



#%% Plot delay between cases and deaths

# parameters for comparison
lag = 12
cfr = 0.013

# Positives by test date and deaths by death date
pos_df = covid.scrape_widash_postest()
death_df = covid.scrape_widash_deaths()

# Combine in one DF
pos_lag = pos_df[['Date', 'Positive']]
pos_lag.Date = pos_lag.Date + datetime.timedelta(days=lag)
lagcol = 'Positive tests +' + str(lag) + ' days'

plotdata = pos_df.set_index('Date')
plotdata[lagcol] = pos_lag.set_index('Date')['Positive']
plotdata['Deaths'] = death_df.set_index('Date')['Total']
plotdata = plotdata.reset_index()


# Make a plot
plotpath = '.\\docs\\_includes\\plotly'
savefile = plotpath+'\\Cases-Deaths-WI.html'


fig = covid.plotly_twolines(
    plotdata, 
    'Deaths',
    lagcol, 
    plotcolors=['firebrick', 'steelblue', 'rosybrown'],
    secondary_scale=1/cfr,
    # date_min=datetime.datetime(2021,1,15),
    range_max=90,
    col1_mode='avg-bar',
    col2_mode='avg',
    plotlabels = {'title': 'Deaths vs Positive tests - WI',
                  'yaxis': 'Deaths',
                  'yaxis_secondary': 'Positive tests',
                  },
    savefile=savefile,
    showfig=False,
    )

fig.update_xaxes(title_text='Date of death')
# fig.update_yaxes(secondary_y=True, tickformat=',.0%')
# fig.update_traces(secondary_y=True, hovertemplate='%{y:.1%}')

fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)

#%%
exit


#%%


# add deaths; set index as date temporarily so they merge correctly
cases = cases.set_index('Date')
temp_deaths = covid.read_deathdate_wi(death_filename).set_index('Date')
cases[death_latest] = temp_deaths['Confirm + Probable deaths']

# add reported cases
cases['Cases (reported)'] = state.set_index('Date').Cases
cases['Deaths (reported)'] = state.set_index('Date').Deaths

# # switch to reported
# case_latest = 'Cases (reported)'
# death_latest = 'Deaths (reported)'

# state
lag = 14
cfr = 0.012

# # Milwaukee
# lag = 16
# cfr = 0.01

death2 = cases[death_latest].reset_index(drop=False)
death2['Date'] = death2['Date'] - datetime.timedelta(days=lag)
cases[death_latest] = death2.set_index('Date')[death_latest] / cfr

cases = cases.rolling(7).mean()
cases = cases.reset_index(drop=False)

# cases.plot(x='Date', y=[case_latest, 'Cases (reported)'])

# cases.plot(x='Date', y=[case_latest, death_latest])



fig = px.line(
    cases, 
    x='Date',
    y=[case_latest, death_latest], 
    color_discrete_sequence=['steelblue', 'firebrick'],
    title='Cases by test date vs Deaths by death date<br>'
          +'(7-day avg, 14-day lag, CFR 1.2%)',
    labels={'value': 'Cases / day'}
    )
fig.update_layout(legend_title='')

pngfile = 'docs\\assets\\Cases-Deaths-Match_2021-04-15.png'
fig.write_image(
    pngfile,
    width=700,
    height=500,
    engine='kaleido',
    )
os.startfile(pngfile)




#%% Map plot for increasing cases


# #%% Get the coviddata
# # Updated by UpdateData.py, just load from csv here

# datapath = '.\\data'
# csv_file_pop = datapath + '\\Population-Data-WI.csv'

# # population data
# popdata = covid.read_pop_data_wi(csv_file_pop)

# # covid data
# widata = covid.read_covid_data_wi('county')


# #%% Geography work

# # shapefile from US census - doesn't have lake winnebago which is annoying
# shapefile = 'data\\geo\\cb_2019_us_county_500k.shp'
# # read data set of all USA counties
# countiesUSA = gpd.read_file(shapefile)
# # filter on wisconsin
# countiesWI = countiesUSA[countiesUSA.STATEFP == '55']

# # reindex on county name
# countiesWI = countiesWI.set_index('NAME')
# # sort by name
# countiesWI = countiesWI.sort_index()
# # add Population column
# countiesWI['Population'] = popdata


# #%% Prep the data


# # reduce and rename columns
# col_rename = {'Date': 'Date', 'NAME': 'County', 'POS_NEW': 'Cases'}
# reduced = widata[col_rename.keys()]
# reduced = reduced.rename(columns=col_rename)

# avg_window = 14

# # isolate cases
# cases = reduced.pivot(index='Date', columns='County', values='Cases')
# cases_avg = cases.rolling(window=avg_window, center=False).mean()
# currcases = cases_avg.iloc[-1]
# pastcases = cases_avg.iloc[-1-avg_window]

# # set any negative values to 0
# def zeroneg(x):
#     if x > 0:
#         return x
#     else:
#         return 0
    
# countiesWI['Cases'] = currcases.apply(zeroneg)
# countiesWI['Past cases'] = pastcases.apply(zeroneg)

# countiesWI['Cases per 100K'] = countiesWI['Cases'] / countiesWI['Population'] * 100000

# # get latitude and longitude of centroids of counties for plotting
# # this will give warning but I don't care
# countiesWI['plotlon'] = countiesWI.geometry.centroid.x
# countiesWI['plotlat'] = countiesWI.geometry.centroid.y
# # move Milwaukee's plot center to the right a bit to make more room for its bubble
# countiesWI.loc['Milwaukee', 'plotlon'] = countiesWI.loc['Milwaukee', 'plotlon'] + 0.07

# # append 'County' for display names
# display_names = [n + ' County' for n in countiesWI.index]

# # set scales for sizes of bubbles
# popscale = 300

# # cases_size_factor = 0.06
# cases_size_factor = 0.06

# cases_color_range = [0,15]

# #%% Change bubble map


# def plotly_changebubble(
#         geodata,
#         currcol,
#         pastcol,
#         colorcol,
#         popcol='Population',
#         size_factor=1,
#         color_range=[0, 600],
#         colorscale=None,
#         location_names=None,
#         plotlabels=None,
#         savefile='.\\temp.html',
#         fig_height='100%',
#         showfig = True,
#         ):
#     """Create interactive plotly map figure, with bubbles that show size and color
    
#     geodata     -- GeoPandas DataFrame 
#     currcol     -- Column to use for current bubble sizes
#     pastcol     -- Column to use for past bubble sizes
#     colorcol    -- Column to use for bubble color
#     fig_height  -- html tag for height of the figure. Default is to fill the div; could also specify pixels.
#     showfig     -- flag for displaying the figure after it is created
#     """
#     # Input process plotlabels
#     plotlabels_default = dict(title='Color-Bubble Map',
#                               sizelabel=currcol,
#                               colorlabel=colorcol,
#                               sizelegend=currcol,
#                               colorlegend=colorcol,
#                               )
#     if plotlabels is not None:
#         # replace default values with the passed values
#         for n in plotlabels.keys():
#             plotlabels_default[n] = plotlabels[n]
#     # then overwrite
#     plotlabels = plotlabels_default
    

#     # Colors for the background map (not used) and marker lines
#     line_colors = {'land':'lightgray', 'border':'darkgray', 'marker':'dimgray', 'past': 'gray'}
    
    
#     # Background map
#     fig = covid.plotly_backmap(geodata)
    
#     fig.update_layout(title=plotlabels['title'])
    
    
#     # Get latitude and longitude of centroids for plotting the bubbles, 
#     # if not already set.
#     # This will give warning but I don't care
#     if 'plotlon' not in geodata.columns:
#         geodata['plotlon'] = geodata.geometry.centroid.x
#     if 'plotlat' not in geodata.columns:
#         geodata['plotlat'] = geodata.geometry.centroid.y    
    
#     # Create display names for tooltip
#     if location_names is None:
#         location_names = geodata.index
#     # Convert to numpy array so can be logically indexed
#     location_names = np.array(location_names)
        
#     # Set any values < 0 to 0
#     geodata[currcol] = geodata[currcol].apply(lambda x: max(x,0))
    
#     # Sort increased and decreased locations
#     # Have both a proportional threshold and an absolute number threshold for
#     # when to display a concentric circle for change vs. only one circle for
#     # negligible change.
#     threshold = 0.3
#     minchange = 10*size_factor
#     increasefrac = geodata[currcol] / geodata[pastcol]
#     increaseabs = abs(geodata[currcol] - geodata[pastcol])
#     pick_increased = np.array((increasefrac > (1+threshold)) & (increaseabs > minchange))
#     pick_decreased = np.array((increasefrac < (1-threshold) ) & (increaseabs > minchange))
#     pick_neither = ~(pick_increased | pick_decreased)
#     increased = geodata[pick_increased]
#     decreased = geodata[pick_decreased]
#     neither   = geodata[pick_neither]


#     # Create bubbles for increased locations
#     # Outer - red, current numbers
#     fig.add_trace(
#         go.Scattergeo(
#             lon=increased.plotlon,
#             lat=increased.plotlat,
#             text=location_names[pick_increased],
#             customdata=increased[popcol],
#             marker=dict(
#                 size=increased[currcol], 
#                 sizeref=size_factor,
#                 sizemode='area',
#                 color='darkmagenta',
#                 # color=increased[colorcol],
#                 # cmin=color_range[0],
#                 # cmax=color_range[1],
#                 # colorscale='Reds',
#                 opacity=0.7,
#                 ),
#             line=dict(color=line_colors['marker']),
#             # hovertemplate=
#             #     '<b>%{text}</b><br>' +
#             #     'Population: %{customdata:.0f}<br>' +
#             #     plotlabels['sizelabel']  + ' : %{marker.size:.1f}<br>' + 
#             #     plotlabels['colorlabel'] + ' : %{marker.color:.1f}'+
#             #     '<extra></extra>',
#                 # No hover info, it was included in the previous bubble plot
#             hovertemplate=None,
#             hoverinfo='skip', 
#             showlegend=True,
#             legendgroup='Increasing',
#             name='Increasing',
#             )
#         )    
#     # Inner - blue, past numbers
#     fig.add_trace(
#         go.Scattergeo(
#             lon=increased.plotlon,
#             lat=increased.plotlat,            
#             text=location_names[pick_increased],
#             customdata=increased[popcol],
#             marker=dict(
#                 size=increased[pastcol], 
#                 sizeref=size_factor,
#                 sizemode='area',
#                 # color='white',
#                 color=increased[colorcol],
#                 cmin=color_range[0],
#                 cmax=color_range[1]*1.1,    # times 1.x to make the color lighter, to make up for the overlap over the existing marker
#                 colorscale=colorscale,
#                 opacity=1,
#                 # colorbar=dict(
#                 #     title=plotlabels['colorlabel'],
#                 #     yanchor='bottom',
#                 #     y=0.6,
#                 #     len=0.25,
#                 #     thickness=12,
#                 #     ),
#                 ),
#             line=dict(color=line_colors['past']),
#             hovertemplate=
#                 '<b>%{text}</b><br>' +
#                 'Population: %{customdata:.0f}<br>' +
#                 plotlabels['sizelabel']  + ' : %{marker.size:.1f}<br>' + 
#                 plotlabels['colorlabel'] + ' : %{marker.color:.1f}'+
#                 '<extra></extra>',
#                 # No hover info, it was included in the previous bubble plot
#             # hovertemplate=None,
#             # hoverinfo='skip', 
#             showlegend=False,
#             legendgroup='Increasing',
#             )
#         )    
    
#     # Create bubbles no change locations
#     fig.add_trace(
#         go.Scattergeo(
#             lon=neither.plotlon,
#             lat=neither.plotlat,
#             text=location_names[pick_neither],
#             customdata=neither[popcol],
#             marker=dict(
#                 size=neither[currcol], 
#                 sizeref=size_factor,
#                 sizemode='area',
#                 color=neither[colorcol],
#                 cmin=color_range[0],
#                 cmax=color_range[1],
#                 colorscale=colorscale,
#                 opacity=0.8,
#                 colorbar=dict(
#                     title=plotlabels['colorlabel'],
#                     yanchor='bottom',
#                     y=0.6,
#                     len=0.25,
#                     thickness=12,
#                     ),
#                 ),
#             line=dict(color=line_colors['marker']),
#             hovertemplate=
#                 '<b>%{text}</b><br>' +
#                 'Population: %{customdata:.0f}<br>' +
#                 plotlabels['sizelabel']  + ' : %{marker.size:.1f}<br>' + 
#                 plotlabels['colorlabel'] + ' : %{marker.color:.1f}'+
#                 '<extra></extra>',
#             showlegend=True,
#             legendgroup='Steady',
#             name='Steady',
#             )
#         )
    
#     # Create bubbles for decreased locations
#     # Outer - past data
#     fig.add_trace(
#         go.Scattergeo(
#             lon=decreased.plotlon,
#             lat=decreased.plotlat,
#             customdata=decreased[popcol],
#             marker=dict(
#                 size=decreased[pastcol], 
#                 sizeref=size_factor,
#                 sizemode='area',
#                 color='rgba(255,255,255,0.3)',  # low opacity for fill
#                 # color=decreased[colorcol],
#                 # cmin=color_range[0],
#                 # cmax=color_range[1],
#                 # colorscale='Greys',
#                 ),
#             line=dict(color=line_colors['past']),
#             # No hover info, it will be included in the next bubble plot
#             hovertemplate=None,
#             hoverinfo='skip', 
#             showlegend=True,
#             legendgroup='Decreasing',
#             name='Decreasing'
#             )
#         )    
    
#     # Inner - current data
#     fig.add_trace(
#         go.Scattergeo(
#             lon=decreased.plotlon,
#             lat=decreased.plotlat,
#             text=location_names[pick_decreased],
#             customdata=decreased[popcol],
#             marker=dict(
#                 size=decreased[currcol], 
#                 sizeref=size_factor,
#                 sizemode='area',
#                 color=decreased[colorcol],
#                 cmin=color_range[0],
#                 cmax=color_range[1],
#                 colorscale=colorscale,
#                 opacity=0.8,
#                 colorbar=dict(
#                     title=plotlabels['colorlabel'],
#                     yanchor='bottom',
#                     y=0.6,
#                     len=0.25,
#                     thickness=12,
#                     ),
#                 ),
#             line=dict(color=line_colors['marker']),
#             hovertemplate=
#                 '<b>%{text}</b><br>' +
#                 'Population: %{customdata:.0f}<br>' +
#                 plotlabels['sizelabel']  + ' : %{marker.size:.1f}<br>' + 
#                 plotlabels['colorlabel'] + ' : %{marker.color:.1f}'+
#                 '<extra></extra>',
#             showlegend=False,
#             legendgroup='Decreasing',
#             )
#         )    
    
#     # Add bubble legend (using dummy traces)  
#     # find dummy locations - put outside the map and hide with a white circle
#     lon_range = np.abs(geodata.plotlon.max() - geodata.plotlon.min())
#     idx = geodata.plotlon.idxmax()   
#     dummy_lon = geodata.plotlon[idx] + 0.1*lon_range
#     dummy_lat = geodata.plotlat[idx]
    
    
    
#     # Bubble legend 
#     # covid.plotly_add_bubblelegend(
#     #     fig, 
#     #     sizeref=size_factor, 
#     #     dummy_lon=dummy_lon, 
#     #     dummy_lat=dummy_lat, 
#     #     colorscale=colorscale,
#     #     line_color=line_colors['marker'],
#     #     legendgroup=None,
#     #     )     
        
#     # Legend title
#     fig.update_layout(
#         legend_title_text=plotlabels['sizelabel'], 
#         # legend_itemclick=False,
#         # legend_itemdoubleclick=False,
#         )
    
#     fig.update_layout(legend_itemsizing='constant')
    
#     # change margins to smaller than default to get map to be bigger
#     fig.update_layout(margin=dict(l=30,b=20))
    
#     # Only display this specific geography, not whole world
#     fig.update_geos(fitbounds='locations', visible=False)
    
#     # plot and save as html, with plotly JS library loaded from CDN
#     fig.write_html(
#         file=savefile,
#         default_height=fig_height,
#         include_plotlyjs='cdn',
#         )      
    
#     # show the figure
#     if showfig:
#         os.startfile(savefile)
    
#     return fig




# #%% Cases figure
# plotly_changebubble(
#     countiesWI,
#     currcol='Cases',
#     pastcol='Past cases',
#     colorcol='Cases per 100K',
#     size_factor=cases_size_factor,
#     color_range=cases_color_range,
#     colorscale='Blues',
#     location_names=display_names,
#     plotlabels=dict(title='Change in Cases by County<br>(by 14-day avg)', sizelabel='Cases'),
#     savefile='.\\docs\\_includes\\plotly\\Map-CaseChange-WI.html',
#     fig_height=600,
#     showfig=True,
#     )



