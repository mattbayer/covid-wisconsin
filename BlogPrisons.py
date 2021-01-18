# -*- coding: utf-8 -*-
"""
Blog on Prisons

Created on Tue Jan 12 17:21:03 2021

@author: 212367548
"""

import pandas as pd
import plotly.express as px
import geopandas as gpd
from plotly.offline import plot as pplot
import plotly.graph_objects as go
import numpy as np
import os
import json

import covid

#%%

prisons_file = '.\\data\\prisons\\prisons-covid-wi.csv'

prisons = pd.read_csv(prisons_file)

#%% Scatter plots

# Infection % vs overcrowding
fig = px.scatter(
    prisons,
    x='% crowded',
    y='% infected',
    title='Infection % vs Crowding',
    # text='Short Name',    
    )

# fig.update_traces(textposition='middle right')

pplot(fig, 
      filename='.\\docs\\assets\\plotly\\Prisons-Crowded.html',
      include_plotlyjs='cdn',
      )

# Infection % vs size
fig = px.scatter(
    prisons,
    x='Total population',
    y='% infected',
    title='Infection % vs Population',
    # text='Short Name',
    )

# fig.update_traces(textposition='middle right')

pplot(fig, 
      filename='.\\docs\\assets\\plotly\\Prisons-Population.html',
      include_plotlyjs='cdn',
      )


#%% Modified map functions



def plotly_colorbubble2(
        geo_background,
        geodata,
        sizecol,
        colorcol,
        latcol,
        loncol,
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
    sizecol     -- Column to use for bubble sizes
    colorcol    -- Column to use for bubble color
    fig_height  -- html tag for height of the figure. Default is to fill the div; could also specify pixels.
    showfig     -- flag for displaying the figure after it is created
    """
    # Input process plotlabels
    plotlabels_default = dict(title='Color-Bubble Map',
                              sizelabel=sizecol,
                              colorlabel=colorcol,
                              sizelegend=sizecol,
                              colorlegend=colorcol,
                              )
    if plotlabels is not None:
        # replace default values with the passed values
        for n in plotlabels.keys():
            plotlabels_default[n] = plotlabels[n]
    # then overwrite
    plotlabels = plotlabels_default
    
    # Plot background map
    fig = covid.plotly_backmap(geo_background)
    # fig = go.Figure()
    
    # # Plotly needs a JSON format string for plotting arbitrary shapes, so -
    # # convert geodata to JSON format string, then decode to dictionary with json.loads()
    # geoJS = json.loads(geo_background.to_json())

    # Colors for the background map
    line_colors = {'land':'lightgray', 'border':'darkgray', 'marker':'dimgray'}
    
    # # Background map
    # fig = px.choropleth(
    #     geo_background, 
    #     geojson=geoJS,
    #     locations=geo_background.index,
    #     color_discrete_sequence=[line_colors['land']],

    #     projection='mercator',
    #     )
    
    # # turn off hover tooltips for this layer - have to set both of these because
    # # hovertemplate is set automatically and it supersedes hoverinfo.
    # # Also take out legend because it's not very useful right now; I could add
    # # a fancier custom legend later.
    # fig.update_traces(
    #     hovertemplate=None, 
    #     hoverinfo='skip', 
    #     marker_line_color=line_colors['border'],
    #     showlegend=False,
    #     )

    fig.update_layout(title=plotlabels['title'])
    
    
    # # Get latitude and longitude of centroids for plotting the bubbles
    # # This will give warning but I don't care
    # geodata['plotlon'] = geodata.geometry.centroid.x
    # geodata['plotlat'] = geodata.geometry.centroid.y    
    
    # Create display names for tooltip
    if location_names is None:
        location_names = geodata.index
    
    # Create the bubble figure
    fig.add_trace(
        go.Scattergeo(
            lon=geodata[loncol],
            lat=geodata[latcol],
            text=location_names,
            marker=dict(
                # symbol='line-ns',
                size=geodata[sizecol], 
                sizeref=size_factor,
                sizemode='area',
                color=geodata[colorcol],
                cmin=color_range[0],
                cmax=color_range[1],
                colorscale=colorscale,
                # opacity=1,
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
            name=sizecol,
            showlegend=False,
            legendgroup=sizecol,
            )
        )
    
    # Add artificial traces to create a legend
    # Max size in pixels from web search and experiment; 
    # then convert to sizes in the units of the sizecol
    legend_marker_pixel_max = 16    # diameter
    legend_marker_sizecol_max = (legend_marker_pixel_max)**2 * size_factor / 2   
    sizes_sizecol = np.array([1, 0.25]) * legend_marker_sizecol_max
    # round to nearest first significant digit
    power10 = 10**np.floor(np.log10(sizes_sizecol))
    sizes_sizecol = np.round(sizes_sizecol / power10) * power10
    # round up to whole integer in case lowest is < 1
    sizes_sizecol = np.ceil(sizes_sizecol)
    # convert to pixel diameter scale
    sizes_pixel = np.round(np.sqrt(sizes_sizecol/size_factor*2))
    # create text labels
    sizes_names = [str(int(s)) for s in sizes_sizecol]
    
    # find dummy locations - put outside the map and hide with a white circle
    lon_range = np.abs(geodata[loncol].max() - geodata[loncol].min())
    idx = geodata[loncol].idxmax()   
    dummy_lon = geodata[loncol][idx] + 0.1*lon_range
    dummy_lat = geodata[latcol][idx]
    
    for ss in range(len(sizes_pixel)):
        fig.add_trace(
            go.Scattergeo(
                lon=[dummy_lon],    # just dummy locations
                lat=[dummy_lat],
                name=sizes_names[ss],
                # visible='legendonly',
                marker=dict(
                    size=sizes_pixel[ss],
                    sizemode='area',
                    color=[(color_range[0]+color_range[1])/2],  # enclose in list so it interprets as data not literal color
                    cmin=color_range[0],
                    cmax=color_range[1],
                    colorscale=colorscale,
                    # opacity=0.5,
                    line=dict(color=line_colors['marker'], width=1),
                    ),
                showlegend=True,
                legendgroup=sizecol,
                hovertemplate=None, 
                hoverinfo='skip', 
                )
            )
    # plot a white marker over the top to hide them
    fig.add_trace(
        go.Scattergeo(
            lon=[dummy_lon],
            lat=[dummy_lat],
            marker=dict(
                size=legend_marker_pixel_max+3,
                color='white',  
                opacity=1,
                ),
            showlegend=False,
            legendgroup='camouflage',
            hovertemplate=None, 
            hoverinfo='skip', 
            ),
        )
        
        
    # Title
    fig.update_layout(
        legend_title_text=plotlabels['sizelabel'], 
        legend_itemclick=False,
        legend_itemdoubleclick=False,
        )
    
    fig.update_layout(legend_itemsizing='trace')
    
    # change margins to smaller than default to get map to be bigger
    fig.update_layout(margin=dict(l=30,b=20))
    
    # Only display this specific geography, not whole world
    # fig.update_geos(fitbounds='locations', visible=False)
    
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

# function for adding bubble legened
# still needs work to make it an independent function... need to be able 
# to pull marker colors from the fig somehow so I don't have to pass
# them in?
def plotly_add_bubblelegend(fig, sizeref, dummy_lon, dummy_lat, fill_color, line_color, legendgroup=None):
    # Add artificial traces to create a legend
    
    # Max size in pixels from web search and experiment; 
    # then convert to sizes in the units of the bubble plot
    legend_marker_pixel_max = 16    # diameter
    legend_marker_size_max = (legend_marker_pixel_max)**2 * sizeref / 2   
    sizes_marker = np.array([1, 0.25]) * legend_marker_size_max
    # round to nearest first significant digit
    power10 = 10**np.floor(np.log10(sizes_marker))
    sizes_marker = np.round(sizes_marker / power10) * power10
    # round up to whole integer in case lowest is < 1
    sizes_marker = np.ceil(sizes_marker)
    # convert to pixel diameter scale
    sizes_pixel = np.round(np.sqrt(sizes_marker/sizeref*2))
    # create text labels
    sizes_names = [str(int(s)) for s in sizes_marker]
    
    if legendgroup is not None:
        # create dummy trace with group title
        fig.add_trace(
            go.Scattergeo(
                lon=[dummy_lon],    # just dummy locations
                lat=[dummy_lat],
                name='<br>'+legendgroup,
                marker=dict(size=0, opacity=0),
                showlegend=True,
                legendgroup=legendgroup,
                hovertemplate=None, 
                hoverinfo='skip', 
                )
            )
            
    # create dummy bubbles with the sizes required
    for ss in range(len(sizes_pixel)):
        fig.add_trace(
            go.Scattergeo(
                lon=[dummy_lon],    # just dummy locations
                lat=[dummy_lat],
                name=sizes_names[ss],
                # visible='legendonly',
                marker=dict(
                    size=sizes_pixel[ss],
                    sizemode='area',
                    color=fill_color,
                    # opacity=0.5,
                    line=dict(color=line_color, width=1),
                    ),
                showlegend=True,
                legendgroup=legendgroup,
                hovertemplate=None, 
                hoverinfo='skip', 
                )
            )
    # plot a white marker over the top to hide them
    fig.add_trace(
        go.Scattergeo(
            lon=[dummy_lon],
            lat=[dummy_lat],
            marker=dict(
                size=legend_marker_pixel_max+3,
                color='white',  
                opacity=1,
                ),
            showlegend=False,
            legendgroup='camouflage',
            hovertemplate=None, 
            hoverinfo='skip', 
            ),
        )     

def plotly_fillbubble(
        geo_background,
        geodata,
        outercol,
        innercol,
        latcol,
        loncol,
        size_factor=1,
        location_names=None,
        plotlabels=None,
        savefile='.\\temp.html',
        fig_height='100%',
        showfig = True,
        ):
    """Create interactive plotly map figure, with concentric bubbles.
    The outer bubble is a max value, and the inner fills it up so this kind of
    map can show a value and a percentage at the same time.
    
    geodata     -- GeoPandas DataFrame 
    outercol    -- Column to use for outer bubble size
    innercol    -- Column to use for inner bubble size, should be < outer.
    fig_height  -- html tag for height of the figure. Default is to fill the div; could also specify pixels.
    showfig     -- flag for displaying the figure after it is created
    """
    # Input process plotlabels
    plotlabels_default = dict(title='Fill-Bubble Map',
                              outerlabel=outercol,
                              innerlabel=innercol,
                              outerlegend=outercol,
                              innerlegend=innercol,
                              )
    if plotlabels is not None:
        # replace default values with the passed values
        for n in plotlabels.keys():
            plotlabels_default[n] = plotlabels[n]
    # then overwrite
    plotlabels = plotlabels_default
    
    # Plot background map
    fig = covid.plotly_backmap(geo_background)
    
    # Colors for the background map
    line_colors = {'land':'lightgray', 'border':'darkgray', 'marker':'dimgray',
                   'outer':'white', 'inner':'orange'}
    
    # Add title
    fig.update_layout(title=plotlabels['title'])   

    # Add bubble legends - do this first so they don't overlap any later markers  
    # first find dummy locations for bubble legend dummy markers - put outside the map and hide with a white circle
    lon_range = np.abs(geodata[loncol].max() - geodata[loncol].min())
    idx = geodata[loncol].idxmax()   
    dummy_lon = geodata[loncol][idx] + 0.1*lon_range
    dummy_lat = geodata[latcol][idx]
        
    # bubble legend for outer bubble
    plotly_add_bubblelegend(
        fig, 
        sizeref=size_factor, 
        dummy_lon=dummy_lon, 
        dummy_lat=dummy_lat, 
        fill_color=line_colors['outer'],
        line_color=line_colors['marker'],
        legendgroup=outercol,
        )
    
    # bubble legend for inner bubble
    plotly_add_bubblelegend(
        fig, 
        sizeref=size_factor, 
        dummy_lon=dummy_lon, 
        dummy_lat=dummy_lat, 
        fill_color=line_colors['inner'],
        line_color='white',
        legendgroup=innercol,
        )

    # Create display names for tooltip
    if location_names is None:
        location_names = geodata.index
    if isinstance(location_names, pd.Series):
        location_names = location_names.to_list()
        
    # create inner and outer bubbles for each data point
    # this is a hack to get the bubbles to overlap correctly - otherwise the 
    # outer bubbles all draw and overlap, then all the inner bubbles draw and 
    # overlap all of those.  I want outer and inner to be drawn and overlap 
    # together.
    geodata = geodata.reset_index()
    for index, row in geodata.iterrows():
        # Create the outer bubble figure
        fig.add_trace(
            go.Scattergeo(
                lon=[row[loncol]],
                lat=[row[latcol]],
                customdata=[row[innercol]],
                text=[row['Name']],
                marker=dict(
                    size=[row[outercol]], 
                    sizeref=size_factor,
                    sizemode='area',
                    color=line_colors['outer'],
                    # opacity=1,
                    ),
                mode='markers',
                line=dict(color=line_colors['marker']),
                hovertemplate=
                    '<b>%{text}</b><br>' +
                    plotlabels['outerlabel']  + ' : %{marker.size:.0f}<br>' + 
                    plotlabels['innerlabel'] + ' : %{customdata:.0f}'+
                    '<extra></extra>',
                name=outercol,
                showlegend=False,
                legendgroup=outercol,
                )
            )
        
        # Create the inner bubble figure
        fig.add_trace(
            go.Scattergeo(
                lon=[row[loncol]],
                lat=[row[latcol]],
                text=[location_names[index]],
                marker=dict(
                    size=[row[innercol]], 
                    sizeref=size_factor,
                    sizemode='area',
                    color=line_colors['inner'],
                    # opacity=1,
                    ),
                mode='markers+text',
                textposition='middle right',
                # line=dict(color=line_colors['marker']),
                # No hover info, it was included in the outer bubble
                hovertemplate=None, 
                hoverinfo='skip', 
                name=innercol,
                showlegend=False,
                legendgroup=innercol,
                )
            )


        
        
    # # Legend Title
    # fig.update_layout(
    #     legend_title_text=plotlabels['outerlabel'], 
    #     # legend_itemclick=False,
    #     # legend_itemdoubleclick=False,
    #     )
    
    fig.update_layout(legend_itemsizing='trace')
    
    # change margins to smaller than default to get map to be bigger
    fig.update_layout(margin=dict(l=30,b=20))
    
    # Only display this specific geography, not whole world
    # fig.update_geos(fitbounds='locations', visible=False)
    
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

#%% Plot map
# read shapefile of all USA counties
countiesUSA = gpd.read_file('data\\geo\\cb_2019_us_county_500k.shp')
# filter on wisconsin
countiesWI = countiesUSA[countiesUSA.STATEFP == '55']

prisons['Fraction infected'] = prisons['Positive Tests'] / prisons['Total population']
prisons = prisons.sort_values('Total population', ascending=False)

# plotly_colorbubble2(
#     countiesWI,
#     prisons,
#     colorcol='Fraction infected',
#     outercol='Total population',
#     loncol='Longitude',
#     latcol='Latitude',
#     popcol='Total population',
#     color_range=[0,1],
#     colorscale='BuPu',
#     location_names=prisons.Name,
#     )

plotly_fillbubble(
    countiesWI,
    prisons,
    outercol='Total population',
    innercol='Positive Tests',
    loncol='Longitude',
    latcol='Latitude',
    location_names=prisons['Short Name'],
    plotlabels=dict(title='Prison Populations and Infections'),
    )