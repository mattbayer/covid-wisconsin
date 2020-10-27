# -*- coding: utf-8 -*-
"""
Created on Wed May 27 20:57:44 2020

@author: Matt Bayer
"""
import datetime
import numpy as np
from scipy import signal
import pandas as pd
import matplotlib.pyplot as plt
import urllib
import os
import plotly
import plotly.graph_objects as go


def plotly_casetest(
        sourcedata,
        case_col,
        test_col,
        plotcolors=['steelblue','olivedrab','lightsteelblue'],
        secondary_scale=10,
        plotlabels = {'title': 'WI Daily Cases and Tests',
                      'yaxis': 'Cases',
                      'yaxis_secondary': 'New people tested',
                      },
        **kwargs,
        ):
    """Create interactive plotly figure for cases and tests.
    
    This is a wrapper for plotly_twolines with two differences. First, column1
    and column2 are renamed to the more explicit case_col and test_col. Second,
    a number of layout parameters are given default values. These layout 
    parameters can still be overridden.
    """      
    plotly_twolines(
        sourcedata,
        case_col,
        test_col,
        plotcolors=plotcolors,
        secondary_scale=secondary_scale,
        plotlabels=plotlabels,
        **kwargs,
        )    
    
def plotly_deadhosp(
        sourcedata,
        dead_col,
        hosp_col,
        plotcolors=['firebrick', 'darkorange', 'rosybrown'],
        secondary_scale=1,
        plotlabels=dict(title='WI Daily Deaths and Hospitalizations',
                        yaxis='Deaths / Hospitalizations',
                        ),
        **kwargs,
        ):
    """Create interactive plotly figure for deaths and hospitalizations.
    
    This is a wrapper for plotly_twolines with two differences. First, column1
    and column2 are renamed to the more explicit dead_col and hosp_col. Second,
    a number of layout parameters are given default values. These layout 
    parameters can still be overridden.
    """      
    plotly_twolines(
        sourcedata,
        dead_col,
        hosp_col,
        plotcolors=plotcolors,
        secondary_scale=secondary_scale,
        plotlabels=plotlabels,
        **kwargs,
        )    

    
def plotly_twolines(
        sourcedata, 
        column1, 
        column2, 
        date_col='Date', 
        plotcolors=None,
        savefile='.\\temp.html',
        groupby=None,
        grouplist=None,
        secondary_scale=1,
        groupcolors=None,
        column1_bar=True,
        plotlabels=None,
        ):
    """Create interactive plotly figure of two quantities.
    
    sourcedata -- a DataFrame containing the data to plot
    column1 -- name of first column to plot
    column2 -- name of second column to plot
    date_col -- name of column containing datetime objects as x-axis
    plotcolors -- colors for the three possible plots, in the order [column1 avg, column2 avg, column1 non-avg]
    savefile -- full path of file for saving the html of the figure
    groupby  -- name of column to use for splitting into a plot grid, such as region
    grouplist -- list of members of groupby to plot. If None then plot first 9.
    secondary_scale -- scale factor of secondary axis, for column2. Max of secondary axis will be (scale) times larger than primary.
    groupcolors -- colors for outlining subplots, corresponding to entries in grouplist
    column1_bar -- if True, plot both an average line and a daily bar chart for column1.  If False, only the line.
    plotlabels -- dict containing strings for 'title', 'yaxis', 'yaxis_secondary'
    """

    # misc input processing - plotcolors
    plotcolors_default = ['black', 'red', 'gray']
    if type(plotcolors_default) is not list:
        plotcolors = plotcolors_default
    elif len(plotcolors) < 3:
        plotcolors_in = plotcolors
        plotcolors = plotcolors_default
        plotcolors[0:len(plotcolors_in)] = plotcolors_in
    # secondary yaxis - if secondary_scale != 1, then have a second y-axis
    secondary_y = (secondary_scale != 1)
    # plotlabels
    if plotlabels is None:
        if secondary_y:
            plotlabels = {'title': column1+' and '+column2, 'yaxis': column1, 'yaxis_secondary': column2}
        else:
            plotlabels = {'title': column1+' and '+column2, 'yaxis': column1+' / '+column2, 'yaxis_secondary': ''}
        
    # input processing for groupby and grouplist
    # make sure grouplist is always a list, even with one element, and 
    # cases/secondary always a 2d DataFrame, even with one column
    if groupby is None:
        grouplist = ['All']
        data1 = pd.DataFrame({'All': sourcedata.set_index(date_col)[column1]})
        data2 = pd.DataFrame({'All': sourcedata.set_index(date_col)[column2]})

    else:
        data1 = sourcedata.pivot(index=date_col, columns=groupby, values=column1)
        data2 = sourcedata.pivot(index=date_col, columns=groupby, values=column2)

        if grouplist is None:
            # take all the columns, or the first 9, whichever is smaller
            grouplist = data1.columns
            if len(grouplist) > 9:
                print('Displaying only the first 9 ' + groupby + 'categories.')
            grouplist = grouplist[0:10]
        elif type(grouplist) is not list:
            grouplist = [grouplist]
            
        data1 = data1[grouplist]
        data2 = data2[grouplist]
        
    # create variables for 7-day average
    avg1 = data1.rolling(window=7, center=False).mean()
    avg2 = data2.rolling(window=7, center=False).mean()

    # create labels
    data1_label = column1
    data2_label = column2
    avg1_label = data1_label + ' (7-day avg)'
    avg2_label = data2_label + ' (7-day avg)'
                
    # create layout of plot grid
    nplots = len(grouplist)      
    ncol = int(np.ceil(np.sqrt(nplots)))
    nrow = int(np.ceil(nplots/ncol))
    
    # make subplot grid
    if nplots > 1:
        sub_titles = grouplist
    else:
        sub_titles = None
        
    sub_spec = [[{"secondary_y": secondary_y}]*ncol]*nrow
    
    fig = plotly.subplots.make_subplots(
        rows=nrow,
        cols=ncol,
        subplot_titles=sub_titles,
        horizontal_spacing=0.05,
        vertical_spacing=0.1,
        specs=sub_spec,
        )
    
    # keep track of row and col of each index plot
    sub_row = [1] * nplots
    sub_col = [1] * nplots
    
    # loop over the plots
    for gg, group in enumerate(grouplist):
        sub_row[gg] = int(gg / ncol) + 1
        sub_col[gg] = gg - (sub_row[gg]-1)*ncol + 1
    
        # only include the very first set of traces in the legend
        if gg == 0:
            showlegend = True
        else:
            showlegend = False
            
        # daily non-avg numbers bar chart for column1
        if column1_bar:
            fig.add_trace(
                go.Bar(
                    x=data1.index, 
                    y=data1.iloc[:,gg],
                    name=data1_label, 
                    marker_color=plotcolors[2], 
                    hovertemplate='%{y:.0f}',
                    showlegend=showlegend,
                    ),
                row=sub_row[gg],
                col=sub_col[gg],
                )
        
        # 7-day average lines           
        fig.add_trace(
            go.Scatter(
                x=avg1.index, 
                y=avg1.iloc[:,gg], 
                name=avg1_label, 
                line_color=plotcolors[0], 
                hovertemplate='%{y:.1f}',
                showlegend=showlegend,
                ),
            row=sub_row[gg],
            col=sub_col[gg],
            secondary_y=False,
            )
        
        fig.add_trace(
            go.Scatter(
                x=avg2.index, 
                y=avg2.iloc[:,gg], 
                name=avg2_label, 
                line_color=plotcolors[1], 
                hovertemplate='%{y:.1f}',
                showlegend=showlegend,
                ),
            row=sub_row[gg],
            col=sub_col[gg],
            secondary_y=secondary_y,
            )
    
    
    # compute y axis range - to_numpy to make robust to multiple columns
    # want secondary to be on a scale exactly 10x primary
    avg1_max = avg1.to_numpy(na_value=0).max()
    avg2_max = avg2.to_numpy(na_value=0).max();
    range_max = max(avg1_max, avg2_max/secondary_scale)
    if column1_bar:
        data1_max = data1.to_numpy(na_value=0).max();
        range_max = max(range_max, data1_max)
    range_y = np.array([-range_max * 0.05, 1.05*range_max])
    
    # compute x axis range - want to extend past the latest date just for viewing niceness
    date_min = avg1.index.min()
    date_max = avg2.index.max() + datetime.timedelta(days=5)
    range_dates = [date_min, date_max]

    # update axes for all plots
    fig.update_xaxes({'range': range_dates}, showticklabels=False)
    fig.update_yaxes({'range': range_y}, secondary_y=False, showticklabels=False)
    # update axes for border plots
    fig.update_xaxes(row=nrow, showticklabels=True)
    fig.update_yaxes(col=1, secondary_y=False, showticklabels=True)
    fig.update_yaxes(col=1, row=int(nrow/2)+1, secondary_y=False, title_text=plotlabels['yaxis'])
    # secondary axis
    if secondary_y:
        fig.update_yaxes({'range': range_y*secondary_scale}, secondary_y=True, showticklabels=False)
        fig.update_yaxes(col=ncol, secondary_y=True, showticklabels=True)
        fig.update_yaxes(col=ncol, row=int(nrow/2)+1, secondary_y=True, title_text=plotlabels['yaxis_secondary'])
    
    # outline subplots in group colors
    if groupcolors is not None:
        if len(groupcolors) == len(grouplist):
            for gg, boxcolor in enumerate(groupcolors):
                rr = sub_row[gg]
                cc = sub_col[gg]
                fig.update_xaxes(showline=True, linewidth=4, linecolor=boxcolor, mirror=True, row=rr, col=cc)
                fig.update_yaxes(showline=True, linewidth=4, linecolor=boxcolor, mirror=True, row=rr, col=cc)
        else:
            raise ValueError('Number of elements in groupcolors does not match number of elements in grouplist.')
    
    fig.update_layout(title_text=plotlabels['title'],
                      hovermode='x unified')
    if nplots == 1:
        fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))     
    else:
        fig.update_layout(legend=dict(orientation='h', yanchor="top", y=-0.18, xanchor="center", x=0.5))     
           
                    
    # plot and save as html, with plotly JS library loaded from CDN
    plotly.offline.plot(fig, 
          filename = savefile, 
          include_plotlyjs='cdn')    
    
    
def plotly_hospdeath(
        data, 
        hosp_col, 
        death_col, 
        date_col='Date', 
        savefile='.\\temp.html',
        groupby=None,
        grouplist=None
        ):
    """Create interactive plotly figure of hospitalizations and deaths
    
    hosp_col -- name of column containing hospitalizations
    death_col -- name of column containing deaths
    date_col -- name of column containing datetime objects as x-axis
    savefile -- full path of file for saving the html of the figure
    groupby  -- name of column to use for splitting into a plot grid, such as region
    grouplist -- list of members of groupby to plot. If None then plot first 9.
    """
    
    # input processing for groupby and grouplist
    # make sure grouplist is always a list, even with one element, and 
    # hosp/tests always a 2d DataFrame, even with one column
    if groupby is None:
        grouplist = ['All']
        hosp = pd.DataFrame({'All': data.set_index(date_col)[hosp_col]})
        deaths = pd.DataFrame({'All': data.set_index(date_col)[death_col]})

    else:
        hosp = data.pivot(index=date_col, columns=groupby, values=hosp_col)
        deaths = data.pivot(index=date_col, columns=groupby, values=death_col)

        if grouplist is None:
            # take all the columns, or the first 9, whichever is smaller
            grouplist = hosp.columns
            if len(grouplist) > 9:
                print('Displaying only the first 9 ' + groupby + 'categories.')
            grouplist = grouplist[0:10]
        elif type(grouplist) is not list:
            grouplist = [grouplist]
            
        hosp = hosp[grouplist]
        deaths = deaths[grouplist]
        
    # create variables for 7-day average
    hosp_avg = hosp.rolling(window=7, center=False).mean()
    deaths_avg = deaths.rolling(window=7, center=False).mean()
    hospavg_label = hosp_col + ' (7-day avg)'
    deathavg_label = death_col + ' (7-day avg)'
                
    # create layout of plot grid
    nplots = len(grouplist)      
    ncol = int(np.ceil(np.sqrt(nplots)))
    nrow = int(np.ceil(nplots/ncol))
    
    # make subplot grid
    if nplots > 1:
        sub_titles = grouplist
    else:
        sub_titles = None
        
    sub_spec = [[{"secondary_y": False}]*ncol]*nrow
    
    fig = plotly.subplots.make_subplots(
        rows=nrow,
        cols=ncol,
        subplot_titles=sub_titles,
        horizontal_spacing=0.05,
        vertical_spacing=0.1,
        specs=sub_spec,
        )
    
    for gg, group in enumerate(grouplist):
        sub_row = int(gg / ncol) + 1
        sub_col = gg - (sub_row-1)*ncol + 1
    
        # only include the very first set of traces in the legend
        if gg == 0:
            showlegend = True
        else:
            showlegend = False
            
        # individual deaths bar chart
        fig.add_trace(
            go.Bar(
                x=deaths.index, 
                y=deaths.iloc[:,gg],
                name=death_col, 
                marker_color='rosybrown', 
                hovertemplate='%{y:.0f}',
                showlegend=showlegend,
                ),
            row=sub_row,
            col=sub_col,
            )
        
        # 7-day average lines           
        fig.add_trace(
            go.Scatter(
                x=deaths_avg.index, 
                y=deaths_avg.iloc[:,gg], 
                name=deathavg_label, 
                line_color='firebrick', 
                hovertemplate='%{y:.1f}',
                showlegend=showlegend,
                ),
            row=sub_row,
            col=sub_col,
            secondary_y=False,
            )

        fig.add_trace(
            go.Scatter(
                x=hosp_avg.index, 
                y=hosp_avg.iloc[:,gg], 
                name=hospavg_label, 
                line_color='darkorange', 
                hovertemplate='%{y:.1f}',
                showlegend=showlegend,
                ),
            row=sub_row,
            col=sub_col,
            secondary_y=False,
            )
    
    
    # compute y axis range - to_numpy to make robust to multiple columns
    # want deaths to be on a scale exactly 10x hosp
    hosp_max = hosp_avg.to_numpy(na_value=0).max()
    deaths_max = deaths_avg.to_numpy(na_value=0).max();
    range_max = max(hosp_max, deaths_max)
    range_hosp = np.array([-range_max * 0.05, 1.05*range_max])
    
    # compute x axis range - want to extend past the latest date just for viewing niceness
    date_min = hosp_avg.index.min()
    date_max = hosp_avg.index.max() + datetime.timedelta(days=5)
    range_dates = [date_min, date_max]

    # update axes for all plots
    fig.update_xaxes({'range': range_dates}, showticklabels=False)
    fig.update_yaxes({'range': range_hosp}, secondary_y=False, showticklabels=False)
    # update axes for border plots
    fig.update_xaxes(row=nrow, showticklabels=True)
    fig.update_yaxes(col=1, title_text='Deaths / Hospitalizations', secondary_y=False, showticklabels=True)
    fig.update_layout(title_text='WI Daily Deaths and Hospitalizations',
                      hovermode='x unified')
    if nplots == 1:
        fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))     
    else:
        fig.update_layout(legend=dict(yanchor="bottom", y=1.04, xanchor="right", x=1))     
           
                    
    # plot and save as html, with plotly JS library loaded from CDN
    plotly.offline.plot(fig, 
          filename = savefile, 
          include_plotlyjs='cdn')    
    

def plot_by_county(datatable, popdata, datatype, n_display=6, county_list=[]):
    """Create stacked line plot of data points by county
    
    datatype -- column name from the datatable
    n_display -- number of plots to display; n_display-1 counties and sum of remainder
    county_list -- list of counties to display, may include 'Other'
    
    If county_list is defined, then plots those counties. You can include 'Other'
    in that list, which will plot the data of all counties not in the list.
    
    If county_list is empty or not defined, then the (n_display - 1) top counties  
    for that datatype are displayed, plus the sum of the remainder as 
    'Other'. 
    """
    selected = select_by_county(datatable, datatype, n_display, county_list)
    selected.columns.name = 'County'
    
    # create 7-day rolling mean
    avg = selected.rolling(window=7, center=True).mean()    

    # stacked line plot
    avg.plot(kind='area')
    plt.title(datatype + ' by county')
    
    # grid of per-capita plots
    per_million = 1e6 * convert_per_capita(avg, popdata)
    fig, axs = plt.subplots(nrows=3, ncols=3, sharex=True, sharey=True, constrained_layout=True)
    for cc, county in enumerate(per_million):
        per_million[county].plot(ax=axs.flat[cc], legend=None)
        axs.flat[cc].set_title(county)
        axs.flat[cc].set_ylabel('Cases / million')
        axs.flat[cc].set_xlabel('Date')
        
    plt.show()
    
def convert_per_capita(countydata, popdata):
    """Convert county-level data to per capita using county population
    
    countydata -- DataFrame with counties in the columns
    popdata -- DataFrame with columns of county and population
    
    countydata may contain an 'Other' column, which should sum the data from 
    all WI counties not otherwise listed in the DataFrame.
    """
    # deep copy of county data to return as per capita
    per_capita = countydata.copy()
    
    # create total pop sum, then iteratively subtract from it to create Other
    pop_other = popdata['WI']    
    
    # loop over all counties except Other
    # first get the counties - this works for MultiIndex columns
    counties = per_capita.columns.get_level_values(0).drop_duplicates()
    # then get rid of 'Other' for now
    all_but_other = [c for c in counties if c != 'Other']
    # do the per-capita division
    for county in all_but_other:
        pop = popdata[county]
        county_series = per_capita[county]
        pop_other = pop_other - pop
        per_capita[county] = county_series / pop
        
    # now take care of Other
    if 'Other' in per_capita:
        per_capita['Other'] = per_capita['Other'] / pop_other
        
    return per_capita
        
# def rank_by_county(datatable, datatype):
    
  
def select_by_county(datatable, datatype,  n_display, county_list=[]):
    """Process data for plotting by county
    
    Select the desired datatype, sort or partition counties, average 7 day.
    
    datatype -- column name from the datatable
    n_display -- number of plots to display; n_display-1 counties and sum of remainder
    county_list -- list of counties to display, may include 'Other'
    
    If county_list is defined, then plots those counties. You can include 'Other'
    in that list, which will plot the data of all counties not in the list.
    
    If county_list is empty or not defined, then the (n_display - 1) top counties  
    for that datatype are displayed, plus the sum of the remainder as 
    'Other'. 
    
    Returns DataFrame with date objects as index, selected counties as columns,
    7-day averaged datatype as data.
    """       
    county_filtered = datatable[datatable.NAME != 'WI']
    
    county_pivot = county_filtered.pivot(index='Date', columns='NAME', values=datatype)
    n_counties = county_pivot.shape[1]
    
    # Select the desired counties
    if len(county_list) > 0:
        # plot counties in the list
        county_select = pd.DataFrame()
        do_other = False
        for county in county_list:
            if county == 'Other':
                # create the Other column with filler data
                do_other = True
                county_select['Other'] = county_pivot.iloc[:,0]
            else:
                # copy this county over
                county_select[county] = county_pivot[county]
                
        if do_other:
            sum_select = county_select.sum(axis=1)
            sum_all = county_pivot.sum(axis=1)
            county_select['Other'] = sum_all - sum_select        
        
    else:
        # sort counties by sum of selected datatype,
        # plot n_display-1 plus sum of remainder in 'Other'
        pivot_summed = county_pivot.sum(axis=0)
        sort_index = pivot_summed.argsort()   
        # flip for descending order 
        pivot_sorted = county_pivot.iloc[:,np.flip(sort_index)] 
    
        # select the top n_display-1 counties, sum the rest together
        if n_display < n_counties:
            # divide into selected and the rest; make sure selected is a copy
            county_select = pd.DataFrame(pivot_sorted.iloc[:, 0:(n_display-1)])
            county_remainder = pivot_sorted.iloc[:, (n_display-1):]
            remainder_sum = county_remainder.sum(axis=1)
            county_select['Other'] = remainder_sum
        else:
            # if the n_display = n_counties, then don't create 'Other' just show all
            county_select = pd.DataFrame(pivot_sorted.iloc[:, 0:n_display])
    
    return county_select
    
                     

def plot_tests_posrate(datatable, location):
    """Create bar plot of tests and positive rate"""
    loc_level = datatable[datatable.NAME == location]
    loc_level = loc_level.sort_values('Date')
    
    dateobjects = loc_level.Date   
 
    # # date index past a starting date
    # datebegin = datetime.datetime(2020, 3, 31)     
    # date_ind = np.repeat(0, len(dateobjects))
    # for dd in range(0, len(dateobjects)):
    #     date_ind[dd] = (dateobjects[dd] >= datebegin)

    positives = np.array(loc_level.POS_NEW);
    tests = np.array(loc_level.TEST_NEW);

    # clean NaN, negative values
    positives[np.isnan(positives)] = 0 
    tests[np.isnan(tests)] = 0
    tests[tests < 0] = 0

    # negatives
    negatives = tests - positives

    # posrate, need some logic to avoid div-0, put nans in right spot
    posrate = np.repeat(0.0, len(positives))
    posrate[tests <= 0] = np.nan
    posrate[tests > 0] = (positives[tests > 0] / tests[tests > 0])    
  
    # create figure and first axis for tests
    fig, ax1 = plt.subplots()
    ax1.bar(dateobjects, positives, width=0.6, color='firebrick')
    ax1.bar(dateobjects, negatives, bottom=positives, width=0.6, color='gray')
    
    # create axis for positive rate
    ax2 = ax1.twinx()
    ax2.plot(dateobjects, posrate, '.-', label='Positive Rate', color='goldenrod', markersize=6)
    ax2.set_ylim((0, ax2.get_ylim()[1]))    
    plt.show()

def select_data(datatable, locations = None, fields=['DTH_NEW', 'POS_NEW', 'TEST_NEW']):
    """Select data and reorganize it.
    
    Returns a DataFrame with Date for index, MultiIndex for columns arranged 
    as select[location][field]
    
    datatable -- Standard DataFrame of covid data
    locations -- String or list of strings for counties or 'WI' to plot 
    fields -- fields of the datatable to include.
    """    
        
    # reorganize the data to MultiIndex in columns
    select = datatable.pivot(index='Date', columns='NAME', values=fields)
    # reorganize the MultiIndex, so it's select[location][field]
    select = select.swaplevel(0,1,axis=1).sort_index(axis='columns', level=0)
    # filter to just the desired locations, if selected
    if locations is not None:
        select = select[locations]
    
    return select

def plotDCT(datatable, locations, per_capita=False, popdata=None):
    """Create line plot comparing deaths, cases, and tests
    
    datatable -- Standard DataFrame of covid data
    locations -- String or list of strings for counties or 'WI' to plot
    per_capita -- Plot according to per capita or raw numbers
    popdata -- population data by location, needed if per_capita is True
    """   
    # catch error if per_capita True but popdata not provided
    if per_capita and popdata is None:
        raise ValueError('The argument popdata must be provided when per_capita=True.')
    
    # for consistency, if locations is a single string make it a one-item list
    if type(locations) == str:
        locations = [locations]
        
    # 3 fields in standard plot
    fields = ['DTH_NEW', 'POS_NEW', 'TEST_NEW']

    # dividing factor for plotting 
    factor = pd.Series({'DTH_NEW':1, 'POS_NEW':10, 'TEST_NEW':100})
    
    # select the data
    filtered = select_data(datatable, locations, fields)
    
    # create 7-day rolling mean
    avg = filtered.rolling(window=7, center=True).mean()    
    
    # per capita or not
    if per_capita:
        leg_labels = ['Deaths per mil', 'Cases per 100k', 'Tests per 10k']
        y_label = 'Deaths per mil'
        # per million
        graphed = 1e6 * convert_per_capita(avg, popdata)
        sharey_setting = True
    else:
        leg_labels = ['Deaths', 'Cases / 10', 'Tests / 100']
        y_label = 'Deaths'
        graphed = avg
        sharey_setting = False
            
    # grid of plots   
    colors = ['firebrick', 'tab:blue', 'goldenrod']

    nrow = 3
    nrow = min(nrow, len(locations))
    ncol = int(np.ceil(len(locations)/nrow))
    nrow = int(np.ceil(len(locations)/ncol))
    fig, axs = plt.subplots(nrows=nrow, ncols=ncol, sharex=True, sharey=sharey_setting, constrained_layout=True)
    # to make code below work for 1x1 plots
    if type(axs) is not np.ndarray:
        axs = np.array(axs)

    for cc, county in enumerate(locations):
        # divide by plotting scale factor
        scaled = graphed[county] / factor
        
        scaled.plot(ax=axs.flat[cc], color=colors, legend=None)
        
        axs.flat[cc].set_title(county)
        axs.flat[cc].set_ylabel(y_label)
        axs.flat[cc].set_xlabel('Date')
    
    # single legend in first axes
    axs.flat[0].legend(leg_labels, loc='upper left')

    plt.show()
    
    
def plot_cases_posrate(datatable, locations, per_capita=False, popdata=None):
    """Create line plot showing cases and positive test rate
    
    datatable -- Standard DataFrame of covid data
    locations -- String or list of strings for counties or 'WI' to plot
    per_capita -- Plot according to per capita or raw numbers
    popdata -- population data by location, needed if per_capita is True
    """   
    # catch error if per_capita True but popdata not provided
    if per_capita and popdata is None:
        raise ValueError('The argument popdata must be provided when per_capita=True.')
    
    # for consistency, if locations is a single string make it a one-item list
    if type(locations) == str:
        locations = [locations]
        
    # 3 fields in standard plot
    fields = ['DTH_NEW', 'POS_NEW', 'TEST_NEW']

    # select the data
    filtered = select_data(datatable, locations, fields)
    
    # create 7-day rolling mean
    avg = filtered.rolling(window=7, center=True).mean()    
       
           
    # per capita or not
    if per_capita:
        leg_labels = ['Cases / million', 'Pos test rate']
        # per million
        # doesn't work - have to figure out how to do per capita with 
        # MultiIndex column names
        graphed = 1e6 * convert_per_capita(avg, popdata)
        sharey_setting = True
    else:
        leg_labels = ['Cases', 'Pos test rate']
        graphed = avg
        sharey_setting = False
        
    # compute positive rate from averaged values
    # done after per-capita to avoid dividing pos rate by population
    # DataFrame has multi-indexed columns, so kind of complicated
    # loop over all counties except Other
    # first get the counties - this works for MultiIndex columns
    counties = avg.columns.get_level_values(0).drop_duplicates()
    for county in counties:
        graphed.loc[:, (county,'PosRate')] = graphed[county]['POS_NEW'] / graphed[county]['TEST_NEW']

            
    # create grid of plots   
    colors = ['tab:blue', 'tab:brown']

    nrow = 3
    nrow = min(nrow, len(locations))
    ncol = int(np.ceil(len(locations)/nrow))
    nrow = int(np.ceil(len(locations)/ncol))
    fig, axs = plt.subplots(nrows=nrow, ncols=ncol, sharex=True, sharey=sharey_setting, constrained_layout=True)
    # to make code below work for 1x1 plots
    if type(axs) is not np.ndarray:
        axs = np.array(axs)

    # loop over counties, create plot for each
    for cc, county in enumerate(locations):
        # select axis
        ax1 = axs.flat[cc]
        # cases plot
        graphed[county].plot(y='POS_NEW', ax=ax1, label=leg_labels[0], color=colors[0], legend=None)
        # pos rate plot on secondary axis
        ax2 = graphed[county].plot(y='PosRate', ax=ax1, label=leg_labels[1], secondary_y=True, color=colors[1], linestyle='--', legend=None)
        
        ax1.set_title(county)
        ax1.set_xlabel('Date')
        ax1.set_ylabel(leg_labels[0])
        ax2.set_ylabel(leg_labels[1])
        ax2.set_ylim(0, 0.25)  # hard coded pos rate y axis 0-25%   
        
    
    # collect line handles and labels for legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    
    # single legend in first axes
    axs.flat[0].legend(lines1 + lines2, labels1 + labels2, loc='upper center')

    plt.show()
    
    
def plot_by_age(datatable):
    """Plot cases and deaths in different age brackets.
    
    This data is only given for Wisconsin as a whole, so no need to specify 
    a location or any other option.
    """
    
    # The data provided is cumulative cases
    # So make new columns for *new* cases in age brackets
    age_suffix = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_59', '60_69', '70_79', '80_89', '90']
    case_cumul_cols = ['POS_' + sfx for sfx in age_suffix]  
    death_cumul_cols = ['DTHS_' + sfx for sfx in age_suffix]
    cumul_cols = case_cumul_cols + death_cumul_cols
    
    # new names for daily data
    case_new_cols = ['POS_NEW_' + sfx for sfx in age_suffix]
    death_new_cols = ['DTH_NEW_' + sfx for sfx in age_suffix]
    new_cols = case_new_cols + death_new_cols
        
    # get cumulative data and compute new-case data
    select = select_data(datatable, 'WI', cumul_cols)
    select[new_cols] = select[cumul_cols].diff()
    
    # relabel and re-bin
    relabel_suffix = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70+']
    
    case_relabels = ['Cases ' + sfx for sfx in relabel_suffix] 
    death_relabels = ['Deaths ' + sfx for sfx in relabel_suffix] 

    select[case_relabels[0:-1]] = select[case_new_cols[0:-3]]
    select[death_relabels[0:-1]] = select[death_new_cols[0:-3]]
    select['Cases 70+'] = select['POS_NEW_70_79'] + select['POS_NEW_80_89'] + select['POS_NEW_90']
    select['Deaths 70+'] = select['DTH_NEW_70_79'] + select['DTH_NEW_80_89'] + select['DTH_NEW_90']
    
    # first 7-day boxcar average for weekly effects, 
    # then 5-day hamming to smooth more
    avg = select.rolling(window=7, center=True).mean()
    avg = avg.rolling(window=5, win_type='hamming', center=True).mean()
        
    # Create cases line plot.  Pretty busy, trying to think of better format...
    ax = avg.plot(y=case_relabels, title='WI smoothed daily cases by age')
    ax.set_ylabel('Cases')

    # Create deaths line plot.  Pretty busy, trying to think of better format...
    ax = avg.plot(y=death_relabels, title='WI smoothed daily deaths by age')
    ax.set_ylabel('Deaths')
    
    

def plot_cases_deaths(datatable, location):
    """Create line plot comparing cases and deaths over time.
    
    location is the string for the geographical region in the data table. 'WI' 
    for whole state, 'Adams' e.g. for a county. TBD for a census tract.
    """
    loc_level = datatable[datatable.NAME == location]

    dateobjects = loc_level.Date
    
    cases = np.array(loc_level.POS_NEW);
    deaths = np.array(loc_level.DTH_NEW);
    
    # create 7-day moving averages
    weights = np.repeat(1,7)/7
    cases_avg = np.convolve(cases, weights, 'valid')
    deaths_avg = np.convolve(deaths, weights, 'valid')
    # make dateobjects for plotting the averages as a *centered* 7-day avg
    dateobjects_avg = dateobjects[3:-3]
    
    # create figure and first axis for cases
    fig, ax1 = plt.subplots()
    ax1.plot(dateobjects, cases, ':', label='Cases', color='mediumblue')
    ax1.plot(dateobjects_avg, cases_avg, '-', label="Cases 7-day Avg", color='mediumblue')
    
    # create second axis for deaths
    ax2 = ax1.twinx()
    ylim1 = ax1.get_ylim();
    ylim2 = (ylim1[0] / 10, ylim1[1] / 10); # deaths plotted at 10x scale of cases
    ax2.plot(dateobjects, deaths, ':', label='Deaths', color='firebrick')
    ax2.plot(dateobjects_avg, deaths_avg, '-', label="Deaths 7-day Avg", color='firebrick')
    ax2.set_ylim(ylim2)
    
    # get legend containing both lines - wow this is kludgy compared to matlab
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # axis labels
    ax1.set_title(location)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Cases')
    ax2.set_ylabel('Deaths')
    
    plt.show()
    
    
def plot_cases_tests(datatable, location):
    """Create line plot comparing cases and tests over time.
    
    location is the string for the geographical region in the data table. 'WI' 
    for whole state, 'Adams' e.g. for a county. TBD for a census tract.
    """
    loc_level = datatable[datatable.NAME == location]

    dateobjects = loc_level.Date
    
    cases = np.array(loc_level.POS_NEW);
    tests = np.array(loc_level.TEST_NEW);
    
    # create 7-day moving averages
    weights = np.repeat(1,7)/7
    cases_avg = np.convolve(cases, weights, 'valid')
    tests_avg = np.convolve(tests, weights, 'valid')
    # make dateobjects for plotting the averages as a *centered* 7-day avg
    dateobjects_avg = dateobjects[3:-3]
    
    # create figure and first axis for cases
    fig, ax1 = plt.subplots()
    ax1.plot(dateobjects, cases, ':', label='Cases', color='mediumblue')
    ax1.plot(dateobjects_avg, cases_avg, '-', label="Cases 7-day Avg", color='mediumblue')

    # create second axis for tests
    ax2 = ax1.twinx()
    ax2.plot(dateobjects, tests, ':', label='Tests', color='goldenrod')
    ax2.plot(dateobjects_avg, tests_avg, '-', label="Tests 7-day Avg", color='goldenrod')

    # scale y limits - start with tests then adjust cases
    ylim1 = ax1.get_ylim();
    ylim2 = ax2.get_ylim();
    maxlim = max(ylim1[1], ylim2[1] / 10)
    ylim1 = (ylim2[0] / 10, ylim2[1] / 10); # tests plotted at 1/10 scale of cases
    ax1.set_ylim(0, maxlim)
    ax2.set_ylim(0, maxlim * 10)
    
    # get legend containing both lines - wow this is kludgy compared to matlab
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # axis labels
    ax1.set_title(location)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Cases')
    ax2.set_ylabel('Tests')
    
    plt.show()
    
   
def download_pop_data_wi(save_file = 'Population-Data-WI.csv'):
    """Download WI population data 
    
    Download an Excel file from a server at the WI Deparment of Administration.
    Parse, then save in simplified csv format.
    """
    # get path and file name root from save_file, to use for intermediate files
    (path, filename) = os.path.split(save_file)
    (root, ext) = os.path.splitext(filename)

    # Download Excel file from the server
    url_pop = 'https://doa.wi.gov/DIR/Final_Ests_Co_2019.xlsx'
    file_excel = os.path.join(path, root + '.xlsx')
    urllib.request.urlretrieve(url_pop, file_excel)
    
    # Parse data into a pandas DataFrame.
    exceldata = pd.read_excel(file_excel, typ='series', orient='index')
    popdata = pd.DataFrame({'County': exceldata.iloc[2:-1, 1], 'Population': exceldata.iloc[2:-1, 2]}, copy=True)
    popdata.reset_index(drop=True)
    
    # Now save that data into a CSV file.
    popdata.to_csv(save_file, index=False)
    
    
def read_pop_data_wi(csv_file = 'Population-Data-WI.csv'):
    """Read previously downloaded WI population data into Series.
    
    Needs some post processing from the CSV format.
    """
    # read CSV data into a DataFrame, then convert to a Series
    popdata_frame = pd.read_csv(csv_file)
    popdata_series = popdata_frame.set_index('County').iloc[:,0]
    
    # add an entry for total WI population
    popdata_series = popdata_series.append(pd.Series({'WI': popdata_series.sum()}))
    
    return popdata_series
    
    
def download_covid_wi_tract(tracts, save_path = '.\\data\\tracts'):
    """Download WI Covid data by census tract, parse, and save to csv file.
    
    Only requests select data fields to limit download size; the other 
    data fields are not currently populated anyway.
    
    tracts -- single string or list of strings, where each string is 
              a 6-digit census tract number for WI
    
    save_path -- path name for CSV file to save the results. Inside this
                 path the file names are hardcoded as 
                 'Covid-Data-WI-Tract-' + tract + '.csv'
    """
    # Check for existence of save_path and create it if it doesn't exist
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    # for consistency, if tracts is a single string make it a one-item list
    if type(tracts) == str:
        tracts = [tracts]
        
    print('Number of tracts:', len(tracts))
        
    for tract in tracts:
        # URL for json request, for specific tract number
        # requesting through GeoServices API, rather than GeoJSON API which 
        # appears to be flaky for filtered requests
        url_root = "https://dhsgis.wi.gov/server/rest/services/DHS_COVID19/COVID19_WI/FeatureServer/10/query?where=GEOID%20%3D%20"
        url_end = "&outFields=*&outSR=4326&f=json"
        # add the tract number, with the constant prefix
        url_tract = url_root + "'55079" + tract + "'" + url_end
    
        # make the request from WI DHS, first to temp file then read in
        # this seems to be more reliable and quicker than going directly to memory
        file_json = os.path.join(save_path, 'temp.geojson')
        
        # urllib.request.urlretrieve(url_tract, file_json)
        jsondata = pd.read_json(url_tract, typ='series', orient='index')
          
        # Parse data into a pandas DataFrame.
        # The JSON file is arranged a little idiosyncratically.
        # The reader function parses the data into a pandas Series of 
        # lists of dictionaries of dictionaries.  The last level of dictionary is 
        # what contains all the data I want to ultimately put into a DataFrame.
        # e.g. jsondata.features[0]['properties']['POSITIVE']   
        # So loop through the useless upper layers of the structure to create a 
        # list of all records.  Then convert that list into a pandas DataFrame.
        data_list = list()
        for record in jsondata.features:
            # data_list.append(record['properties'])
            data_list.append(record['attributes'])
            
        data_table = pd.DataFrame.from_records(data_list)
        
        # Now save that data into a CSV file, which will be much smaller and 
        # easier for a person to read directly.
        save_file = os.path.join(save_path, 'Covid-Data-WI-Tract-' + tract + '.csv')
        data_table.to_csv(save_file, index=False)    
        
        # print to screen to display progress
        print('.', end='')
        
    # print new line to screen to end progress tracker
    print('')
    
    # delete temporary file
    if os.path.exists(file_json):
        os.remove(file_json)
    
        
def download_covid_data_wi(dataset='state'):
    """Download one of the three datasets from WI DHS and return as DataFrame.

    dataset -- 'state', 'county', or 'tract'. Each dataset has its own 
               assortment of data columns.
    """
    url_json_state  = "https://opendata.arcgis.com/datasets/859602b5d427456f821de3830f89301c_11.geojson"
    url_json_county = "https://opendata.arcgis.com/datasets/5374188992374b318d3e2305216ee413_12.geojson"
    url_json_tract  = "https://opendata.arcgis.com/datasets/89d7a90aafa24519847c89b249be96ca_13.geojson"
    
    urls = {'state': url_json_state, 'county': url_json_county, 'tract': url_json_tract}
    
    if dataset not in urls.keys():
        raise ValueError("Dataset not supported. Supported datasets are 'state', 'county', or 'tract'.")
        
    # make the request from WI DHS - directly from url to memory
    jsondata = pd.read_json(urls[dataset], typ='series', orient='index')

    # Parse data into a pandas DataFrame.
    # The JSON file is arranged a little idiosyncratically.
    # The reader function parses the data into a pandas Series of 
    # lists of dictionaries of dictionaries.  The last level of dictionary is 
    # what contains all the data I want to ultimately put into a DataFrame.
    # e.g. jsondata.features[0]['properties']['POSITIVE']   
    # So loop through the useless upper layers of the structure to create a 
    # list of all records.  Then convert that list into a pandas DataFrame.
    data_list = list()
    for record in jsondata.features:
        data_list.append(record['properties'])
        
    data_table = pd.DataFrame.from_records(data_list)
    
    # make sure everything is interpreted as numeric if it can be
    # this is important for consistency with loading from CSV files later
    data_table = data_table.apply(pd.to_numeric, errors='ignore')
    
    return data_table


def update_covid_data_wi(dataset='state', save_path='.\\data'):
    """Update Covid data by downloading recent updates from WI DHS.
    This function downloads updated data, cleans it, then merges it with 
    historical data. It then saves a CSV file of the updated data.
    
    DHS no longer provides data dated back to the beginning of the pandemic, 
    but only the last 90 days. That means I have maintain a historic record 
    and update it from DHS data.
    
    There are three datasets: state, county, and census tract. They each have
    their own data columns. DHS stores them entirely separately. For my data 
    analysis, I want each smaller level of data to contain the higher levels 
    for comparison. So when I update 'county', it will also download 'state'
    and merge it into the county DataFrame, stripping any extra data columns
    that only state has.    
    
    The data path can be specified, but the data file names are hardcoded as
    'Covid-Data-WI-State.csv', 'Covid-Data-WI-County.csv, 'Covid-Data-WI-Tract.csv'
    
    dataset -- 'state', 'county', or 'tract'.
    save_path -- Path for saving the data files.
    """
    # Check for existence of save_path and create it if it doesn't exist
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    filenames = {'state':  'Covid-Data-WI-State.csv',
                 'county': 'Covid-Data-WI-County.csv',
                 'tract':  'Covid-Data-WI-Tract.csv'}
    
    if dataset not in filenames.keys():
        raise ValueError("Dataset not supported. Supported datasets are 'state', 'county', or 'tract'.")
            
    # update and merge state, county, tract in order,stopping at the chosen 
    # dataset
    data_update = download_covid_data_wi('state')
    if dataset == 'county' or dataset == 'tract':
        county_update = download_covid_data_wi('county')
        data_update = pd.concat([data_update, county_update], join='inner')
    if dataset == 'tract':
        tract_update = download_covid_data_wi('tract')
        data_update = pd.concat([data_update, tract_update], join='inner')
    
    # Some limited data cleaning - mainly for NaNs
    # Replace N/A or None objects (for blank data) with NaN
    # Some places also have -999 values, also replace those with NaN
    # More data cleaning is done in read_covid_data_wi, which makes it more 
    # accessible for analysis
    data_update = data_update.fillna(value=np.nan)
    data_update = data_update.replace(to_replace=-999, value=np.nan)

    # Load the historical data, as long as it exists
    path_file = os.path.join(save_path, filenames[dataset])
    if os.path.exists(path_file):
        data_saved = pd.read_csv(path_file) 
        
        # Merge with the update. 
        # First use update() to overwrite any updated data. Need to reindex first.
        data_update = data_update.set_index(['DATE','GEOID'])
        data_saved = data_saved.set_index(['DATE', 'GEOID'])
        data_saved.update(data_update)
        data_update = data_update.reset_index()
        data_saved = data_saved.reset_index()
        # Next do an outer join to get new dates.
        data_update = pd.merge(data_update, data_saved, how='outer') 
        
    # Sort by date and GEOID
    # This makes updates to the CSV file easier to read in diff programs, 
    # since all the changes should be on the bottom.
    data_update = data_update.sort_values(by=['DATE','GEOID'])
    
    # Now save that data into the CSV file.
    save_file = os.path.join(save_path, filenames[dataset])
    data_update.to_csv(save_file, index=False)    
    

def read_covid_data_wi(dataset='county', data_path = '.\\data', csv_file = None):
    """Read previously downloaded WI covid data into DataFrame.
    
    Needs some pre-processing after load.
    - Convert date strings into Python datetime objects.
    
    dataset   -- name of defined data set, 'state', 'county', or 'tract'.
    data_path -- path name for location of CSV data file
    csv_file  -- data file name. If this is defined, it overrides dataset.  
    """
    # Input processing
    filenames = {'state':  'Covid-Data-WI-State.csv',
                 'county': 'Covid-Data-WI-County.csv',
                 'tract':  'Covid-Data-WI-Tract.csv'}
    if csv_file is None:
        if dataset in filenames.keys():
            csv_file = filenames[dataset]
        else:
            raise ValueError("Dataset not supported. Supported datasets are 'state', 'county', or 'tract'.")
    
    # Read from CSV file
    path_file = os.path.join(data_path, csv_file)
    covid_data = pd.read_csv(path_file) 
    
    # Add new column with converted dates
    # LoadDttm contains hour/minute information, the conversion discards that
    covid_data['Date'] = convert_rawdates(covid_data.DATE)
    
    # Make a list of only useful columns
    remove_list = ['OBJECTID','GEOID','GEO','DATE']
    col_list = covid_data.columns.tolist()
    for s in remove_list:
        col_list.remove(s)
    # Take Date from the back and put it on the front
    col_list.insert(0,col_list.pop())   
    # Re-order according to the new list
    covid_data = covid_data[col_list]

    # Create new hospitalizations column by taking difference of HOSP_YES
    if 'HOSP_YES' in col_list:
        covid_data = covid_data.sort_values('Date')
        covid_data = covid_data.assign(HOSP_NEW = covid_data.groupby('NAME').HOSP_YES.diff(periods=1))
    
    # # Make new columns for *new* positives in age brackets
    # age_suffix = ['0_9', '10_19', '20_29', '30_39', '40_49', '50_59', '60_69', '70_79', '80_89', '90']
    # age_cols = ['POS_0_9', 'POS_10_19', 'POS_20_29', 'POS_30_39', 'POS_40_49', 'POS_50_59', 'POS_60_69', 'POS_70_79', 'POS_80_89', 'POS_90']
    # # view by location and data
    # pivot = covid_data.pivot(index='Date', column='')
    # for sfx in age_suffix:
    #     cumul_col = 'POS_' + sfx
    #     new_col = 'POS_NEW_' + sfx
    #     covid_data[new_col] = np.diff(covid_data[cumul_col])
        
    return covid_data
    
    
def download_covid_wi_county(save_path = '.\\data'):
    """Download latest WI Covid data for state and county, parse, 
    and save to csv file.
    
    Note that the URL retrieval will not work behind GE's VPN.
    
    save_path -- path name for CSV file to save the results. Inside this
                 path the file name is hardcoded as 'Covid-Data-WI.csv'
    """
        
    # Check for existence of save_path and create it if it doesn't exist
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    # Download data in JSON format from server and save to current path
    # path = './'
    # URL for json request, filtered to only state and county
    url_json = "https://opendata.arcgis.com/datasets/b913e9591eae4912b33dc5b4e88646c5_10.geojson?where=%20(GEO%20%3D%20'County'%20OR%20GEO%20%3D%20'State')%20"
    # unfiltered, includes census tracts
    # url_json = 'https://opendata.arcgis.com/datasets/b913e9591eae4912b33dc5b4e88646c5_10.geojson'
    # file_json = path + 'Covid-Data-WI.geojson'
    # urllib.request.urlretrieve(url_json, file_json)


    # make the request from WI DHS - directly from url to memory
    jsondata = pd.read_json(url_json, typ='series', orient='index')

    # Parse data into a pandas DataFrame.
    # The JSON file is arranged a little idiosyncratically.
    # The reader function parses the data into a pandas Series of 
    # lists of dictionaries of dictionaries.  The last level of dictionary is 
    # what contains all the data I want to ultimately put into a DataFrame.
    # e.g. jsondata.features[0]['properties']['POSITIVE']   
    # So loop through the useless upper layers of the structure to create a 
    # list of all records.  Then convert that list into a pandas DataFrame.
    data_list = list()
    for record in jsondata.features:
        data_list.append(record['properties'])
        
    data_table = pd.DataFrame.from_records(data_list)
    
    # Now save that data into a CSV file, which will be much smaller and 
    # easier for a person to read directly.
    save_file = os.path.join(save_path, 'Covid-Data-WI-County.csv')
    data_table.to_csv(save_file, index=False)
    
    
    
def update_covid_wi_all(save_path = '.\\data'):
    """Download latest WI Covid data for state, county, and census tract;
    parse, and save to CSV file.
    
    If download from URL does not work, the function checks if a raw JSON file
    exists that is newer than the CSV file, and if so updates the CSV. This 
    allows manual download of the raw data in case of VPN not allowing 
    automated downloads.
    
    save_path -- path name for CSV file to save the results. Inside this
                 path the file names are hardcoded as 'Covid-Data-WI.geojson'
                 and 'Covid-Data-WI.csv'.
    """
        
    # Check for existence of save_path and create it if it doesn't exist
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    # Define required file names    
    file_json = os.path.join(save_path, 'Covid-Data-WI.geojson')
    file_csv = os.path.join(save_path, 'Covid-Data-WI.csv')

    # URL for json request, including state, counties, and tracts
    url_json = 'https://opendata.arcgis.com/datasets/b913e9591eae4912b33dc5b4e88646c5_10.geojson'
    
    # Download data in JSON format from server if possible and download to file
    try:
        urllib.request.urlretrieve(url_json, file_json)
        print('Data URL request successful. Updating CSV file.')
    except:
        # Update request failed.  
        # If the JSON file is newer than the CSV file (such as if it has been
        # manually downloaded), then continue the function. Otherwise exit.
        if not os.path.exists(file_json):
            print('Data URL request failed, and could not find a previous JSON data file. No data update performed.')
            return
        elif os.path.exists(file_csv) and os.path.getmtime(file_csv) > os.path.getmtime(file_json):
            print('Data URL request failed, and CSV data file is up to date with existing JSON file. No data update performed.')
            return
        else:
            print('Data URL request failed, but CSV data file is not up to date with existing JSON file. Updating CSV file.')

    # Read in the JSON file
    jsondata = pd.read_json(file_json, typ='series', orient='index')

    # Parse data into a pandas DataFrame.
    # The JSON file is arranged a little idiosyncratically.
    # The reader function parses the data into a pandas Series of 
    # lists of dictionaries of dictionaries.  The last level of dictionary is 
    # what contains all the data I want to ultimately put into a DataFrame.
    # e.g. jsondata.features[0]['properties']['POSITIVE']   
    # So loop through the useless upper layers of the structure to create a 
    # list of all records.  Then convert that list into a pandas DataFrame.
    data_list = list()
    for record in jsondata.features:
        data_list.append(record['properties'])
        
    data_table = pd.DataFrame.from_records(data_list)
    
    # Now save that data into a CSV file, which will be much smaller and 
    # easier for a person to read directly.
    save_file = os.path.join(save_path, 'Covid-Data-WI.csv')
    data_table.to_csv(save_file, index=False)
    
    

    


def convert_rawdates(rawdates, discard_time=True):
    """Convert raw dates from WI data to date objects.
    
    From the WI data, dates either come in the form of a string or a large
    number of milleseconds. This function figures out which and processes
    accordingly.
    """
    dobj = list()

    if type(rawdates[0]) is str:
        format_str = "%Y/%m/%d %H:%M:%S+00"
        for dstr in rawdates:
            d = datetime.datetime.strptime(dstr, format_str)
            if discard_time:
                d = d.replace(hour=0, minute=0, second=0)
            dobj.append(d)
    else:          
        for dint in rawdates:
            # if a number, then it is in UNIX timestamp format, 
            # but times 1000 for some reason.
            d = datetime.date.fromtimestamp(dint/1000)
            dobj.append(d)  
        
    return dobj