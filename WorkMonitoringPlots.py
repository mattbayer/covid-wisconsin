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


#%% Get positives/tests

"""
pos_df = covid.scrape_widash_postest()

#%% Get reported data and add to pos_df
widata = covid.read_covid_data_wi('state')
pos_df = pos_df.set_index('Date')
pos_df['Reported Cases'] = widata.set_index('Date')['POS_NEW']
pos_df = pos_df.reset_index()
pos_df = pos_df.rename(columns={'Positive': 'Positive tests', 'Percent Positive': 'Percent positive'})

#%% Plotly plot for cases / positivity
plotpath = '.\\docs\\_includes\\plotly'
savefile = plotpath+'\\Cases-Positivity-WI.html'


fig = covid.plotly_twolines(
    pos_df, 
    'Positive tests', 
    # 'Reported Cases', 
    'Percent positive',
    plotcolors=['steelblue', 'darkmagenta', 'lightsteelblue'],
    secondary_scale=1/200,
    date_min=datetime.datetime(2021,1,15),
    range_max=2000,
    col1_mode='avg-bar',
    col2_mode='line',
    plotlabels = {'title': 'WI Positive Tests and Percent Positive',
                  'yaxis': 'Positve tests',
                  'yaxis_secondary': 'Percent positive',
                  },
    savefile=savefile,
    showfig=False,
    )

fig.update_xaxes(title_text='Date of test result')

fig.write_html(
    file=savefile,
    include_plotlyjs='cdn',
    )      
os.startfile(savefile)

"""


#%% Map plot for increasing cases


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


# reduce and rename columns
col_rename = {'Date': 'Date', 'NAME': 'County', 'POS_NEW': 'Cases'}
reduced = widata[col_rename.keys()]
reduced = reduced.rename(columns=col_rename)

avg_window = 7

# isolate cases
cases = reduced.pivot(index='Date', columns='County', values='Cases')
cases_avg = cases.rolling(window=avg_window, center=False).mean()
currcases = cases_avg.iloc[-1]
pastcases = cases_avg.iloc[-8]

# set any negative values to 0
def zeroneg(x):
    if x > 0:
        return x
    else:
        return 0
    
countiesWI['Cases'] = currcases.apply(zeroneg)
countiesWI['Past cases'] = pastcases.apply(zeroneg)

countiesWI['Cases per 100K'] = countiesWI['Cases'] / countiesWI['Population'] * 100000


#%% Bubble map - size is numbers, color is per-population

# get latitude and longitude of centroids of counties for plotting
# this will give warning but I don't care
countiesWI['plotlon'] = countiesWI.geometry.centroid.x
countiesWI['plotlat'] = countiesWI.geometry.centroid.y
# move Milwaukee's plot center to the right a bit to make more room for its bubble
countiesWI.loc['Milwaukee', 'plotlon'] = countiesWI.loc['Milwaukee', 'plotlon'] + 0.07

# append 'County' for display names
display_names = [n + ' County' for n in countiesWI.index]

# set scales for sizes of bubbles
popscale = 300

# cases_size_factor = 0.06
cases_size_factor = 0.06

cases_color_range = [0,20]

#%% Change bubble map


def plotly_changebubble(
        geodata,
        currcol,
        pastcol,
        colorcol,
        popcol='Population',
        size_factor=1,
        color_range=[0, 600],
        colorscale=None,
        location_names=None,
        plotlabels=None,
        savefile='.\\temp.html',
        fig_height='100%',
        showfig = True,
        ):
    """Create interactive plotly map figure, with bubbles that show size and color
    
    geodata     -- GeoPandas DataFrame 
    currcol     -- Column to use for current bubble sizes
    pastcol     -- Column to use for past bubble sizes
    colorcol    -- Column to use for bubble color
    fig_height  -- html tag for height of the figure. Default is to fill the div; could also specify pixels.
    showfig     -- flag for displaying the figure after it is created
    """
    # Input process plotlabels
    plotlabels_default = dict(title='Color-Bubble Map',
                              sizelabel=currcol,
                              colorlabel=colorcol,
                              sizelegend=currcol,
                              colorlegend=colorcol,
                              )
    if plotlabels is not None:
        # replace default values with the passed values
        for n in plotlabels.keys():
            plotlabels_default[n] = plotlabels[n]
    # then overwrite
    plotlabels = plotlabels_default
    

    # Colors for the background map (not used) and marker lines
    line_colors = {'land':'lightgray', 'border':'darkgray', 'marker':'dimgray'}
    
    
    # Background map
    fig = covid.plotly_backmap(geodata)
    
    fig.update_layout(title=plotlabels['title'])
    
    
    # Get latitude and longitude of centroids for plotting the bubbles, 
    # if not already set.
    # This will give warning but I don't care
    if 'plotlon' not in geodata.columns:
        geodata['plotlon'] = geodata.geometry.centroid.x
    if 'plotlat' not in geodata.columns:
        geodata['plotlat'] = geodata.geometry.centroid.y    
    
    # Create display names for tooltip
    if location_names is None:
        location_names = geodata.index
    # Convert to numpy array so can be logically indexed
    location_names = np.array(location_names)
        
    # Set any values < 0 to 0
    geodata[currcol] = geodata[currcol].apply(lambda x: max(x,0))
    
    # Sort increased and decreased locations
    threshold = 0.3
    minchange = 20*size_factor
    increasefrac = geodata[currcol] / geodata[pastcol]
    increaseabs = abs(geodata[currcol] - geodata[pastcol])
    pick_increased = np.array((increasefrac > (1+threshold)) & (increaseabs > minchange))
    pick_decreased = np.array((increasefrac < (1-threshold) ) & (increaseabs > minchange))
    pick_neither = ~(pick_increased | pick_decreased)
    increased = geodata[pick_increased]
    decreased = geodata[pick_decreased]
    neither   = geodata[pick_neither]


    # Create bubbles for increased locations
    # Outer - red, current numbers
    fig.add_trace(
        go.Scattergeo(
            lon=increased.plotlon,
            lat=increased.plotlat,
            text=location_names[pick_increased],
            customdata=increased[popcol],
            marker=dict(
                size=increased[currcol], 
                sizeref=size_factor,
                sizemode='area',
                color=increased[colorcol],
                cmin=color_range[0],
                cmax=color_range[1],
                colorscale='Reds',
                ),
            line=dict(color=line_colors['marker']),
            hovertemplate=
                '<b>%{text}</b><br>' +
                'Population: %{customdata:.0f}<br>' +
                plotlabels['sizelabel']  + ' : %{marker.size:.1f}<br>' + 
                plotlabels['colorlabel'] + ' : %{marker.color:.1f}'+
                '<extra></extra>',
            name=currcol,
            showlegend=False,
            legendgroup=currcol,
            )
        )    
    # Inner - blue, past numbers
    fig.add_trace(
        go.Scattergeo(
            lon=increased.plotlon,
            lat=increased.plotlat,
            # text=location_names,
            customdata=increased[popcol],
            marker=dict(
                size=increased[pastcol], 
                sizeref=size_factor,
                sizemode='area',
                color=increased[colorcol],
                cmin=color_range[0],
                cmax=color_range[1],
                colorscale=colorscale,
                colorbar=dict(
                    title=plotlabels['colorlabel'],
                    yanchor='bottom',
                    y=0.6,
                    len=0.25,
                    thickness=12,
                    ),
                ),
            line=dict(color=line_colors['marker']),
            # No hover info, it was included in the previous bubble plot
            hovertemplate=None,
            hoverinfo='skip', 
            name=currcol,
            showlegend=False,
            legendgroup=currcol,
            )
        )    
    
    # Create bubbles no change locations
    fig.add_trace(
        go.Scattergeo(
            lon=neither.plotlon,
            lat=neither.plotlat,
            text=location_names[pick_neither],
            customdata=neither[popcol],
            marker=dict(
                size=neither[currcol], 
                sizeref=size_factor,
                sizemode='area',
                color=neither[colorcol],
                cmin=color_range[0],
                cmax=color_range[1],
                colorscale=colorscale,
                colorbar=dict(
                    title=plotlabels['colorlabel'],
                    yanchor='bottom',
                    y=0.6,
                    len=0.25,
                    thickness=12,
                    ),
                ),
            line=dict(color=line_colors['marker']),
            hovertemplate=
                '<b>%{text}</b><br>' +
                'Population: %{customdata:.0f}<br>' +
                plotlabels['sizelabel']  + ' : %{marker.size:.1f}<br>' + 
                plotlabels['colorlabel'] + ' : %{marker.color:.1f}'+
                '<extra></extra>',
            name=currcol,
            showlegend=False,
            legendgroup=currcol,
            )
        )
    
    # Create bubbles for decreased locations
    # Outer - past data
    fig.add_trace(
        go.Scattergeo(
            lon=decreased.plotlon,
            lat=decreased.plotlat,
            customdata=decreased[popcol],
            marker=dict(
                size=decreased[pastcol], 
                sizeref=size_factor,
                sizemode='area',
                color='rgba(255,255,255,0.3)',  # low opacity for fill
                # color=decreased[colorcol],
                # cmin=color_range[0],
                # cmax=color_range[1],
                # colorscale='Greys',
                ),
            line=dict(color=line_colors['marker']),
            # No hover info, it will be included in the next bubble plot
            hovertemplate=None,
            hoverinfo='skip', 
            name=currcol,
            showlegend=False,
            legendgroup=currcol,
            )
        )    
    
    # Inner - current data
    fig.add_trace(
        go.Scattergeo(
            lon=decreased.plotlon,
            lat=decreased.plotlat,
            text=location_names[pick_decreased],
            customdata=decreased[popcol],
            marker=dict(
                size=decreased[currcol], 
                sizeref=size_factor,
                sizemode='area',
                color=decreased[colorcol],
                cmin=color_range[0],
                cmax=color_range[1],
                colorscale=colorscale,
                colorbar=dict(
                    title=plotlabels['colorlabel'],
                    yanchor='bottom',
                    y=0.6,
                    len=0.25,
                    thickness=12,
                    ),
                ),
            line=dict(color=line_colors['marker']),
            hovertemplate=
                '<b>%{text}</b><br>' +
                'Population: %{customdata:.0f}<br>' +
                plotlabels['sizelabel']  + ' : %{marker.size:.1f}<br>' + 
                plotlabels['colorlabel'] + ' : %{marker.color:.1f}'+
                '<extra></extra>',
            name=currcol,
            showlegend=False,
            legendgroup=currcol,
            )
        )    
    
    # Add bubble legend (using dummy traces)  
    # find dummy locations - put outside the map and hide with a white circle
    lon_range = np.abs(geodata.plotlon.max() - geodata.plotlon.min())
    idx = geodata.plotlon.idxmax()   
    dummy_lon = geodata.plotlon[idx] + 0.1*lon_range
    dummy_lat = geodata.plotlat[idx]
    
    # Bubble legend 
    covid.plotly_add_bubblelegend(
        fig, 
        sizeref=size_factor, 
        dummy_lon=dummy_lon, 
        dummy_lat=dummy_lat, 
        colorscale=colorscale,
        line_color=line_colors['marker'],
        legendgroup=None,
        )     
        
    # Legend title
    fig.update_layout(
        legend_title_text=plotlabels['sizelabel'], 
        legend_itemclick=False,
        legend_itemdoubleclick=False,
        )
    
    fig.update_layout(legend_itemsizing='trace')
    
    # change margins to smaller than default to get map to be bigger
    fig.update_layout(margin=dict(l=30,b=20))
    
    # Only display this specific geography, not whole world
    fig.update_geos(fitbounds='locations', visible=False)
    
    # plot and save as html, with plotly JS library loaded from CDN
    fig.write_html(
        file=savefile,
        default_height=fig_height,
        include_plotlyjs='cdn',
        )      
    
    # show the figure
    if showfig:
        os.startfile(savefile)
    
    return fig




#%% Cases figure
plotly_changebubble(
    countiesWI,
    currcol='Cases',
    pastcol='Past cases',
    colorcol='Cases per 100K',
    size_factor=cases_size_factor,
    color_range=cases_color_range,
    colorscale='Blues',
    location_names=display_names,
    plotlabels=dict(title='Cases by County<br>(Daily, 7-day avg)'),
    savefile='.\\docs\\_includes\\plotly\\Map-CaseChange-WI.html',
    fig_height=600,
    showfig=True,
    )



