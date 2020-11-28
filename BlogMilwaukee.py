# -*- coding: utf-8 -*-
"""
Create interactive maps for cases and hospitalizations using Plotly.
"""

import pandas as pd
import geopandas as gpd
import datetime
import numpy as np

import covid

import re

#%%

if False:
    # get milwaukee test numbers by copying html of the dashboard and scraping it
    # get this originally by doing a browser html inspection of the graph on the Milwaukee county dashboard,
    # then copying it to a text file.  The tooltips of the graph are stored in "aria-label" labels, so
    # I can regex on these labels below.
    
    
    def parse_mke_dashboard(html_file, data_name):
        file_obj = open(html_file)
        file_text = file_obj.read()
            
        m = re.findall('aria-label=\"\s(\S*?)\s(\S*?)\"', file_text)
        
        datelist = list()
        valuelist = list()
        for kk, element in enumerate(m):
            datestr = element[0]
            date = datetime.datetime(year=2020, month=pd.to_numeric(datestr[0:2]), day=pd.to_numeric(datestr[3:]))
            datelist.append(date)
            
            valuestr = element[1]
            valuestr = valuestr.replace(',', '')
            valuelist.append(pd.to_numeric(valuestr))
            
        data = pd.DataFrame(data={'Date': datelist, data_name: valuelist})
        
        return data
    
    tests = parse_mke_dashboard('C:\dev\covid-wisconsin\data\Dashboard-Milwaukee-Tests_2020-11-09.html', 'Tests')
    cases = parse_mke_dashboard('C:\dev\covid-wisconsin\data\Dashboard-Milwaukee-Cases_2020-11-09.html', 'Cases')
    
    mke = tests.merge(cases)
    mke['Positive Rate'] = mke.Cases / mke.Tests
    
    mke.plot(x='Date', y=['Tests', 'Cases'])
    mke.plot(x='Date', y='Positive Rate')



#%% Get the coviddata
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'
csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
# covid.update_covid_data_wi('tract')
covid_tract = covid.read_covid_data_wi('tract')
county = covid.read_covid_data_wi('county')


# filter on Milwaukee tracts
covid_tract_mke = covid_tract.loc[covid_tract.GEO=='Census tract']
covid_tract_mke = covid_tract_mke.loc[covid_tract_mke.GEOID.apply(lambda x: x[0:5]=='55079')]
    

#%% County racial stats
mke = county.loc[county.NAME == 'Milwaukee']
mke.plot(x='Date', y=['POS_WHT', 'POS_BLK', 'POS_E_HSP'])


#%% Tract population

tractpopfile = '.\\data\\geo\\Tract-Population-WI\\Tract-Population-WI.csv'
tractcsv = pd.read_csv(tractpopfile)
tractpop = pd.DataFrame({'GEOID': [s[9:] for s in tractcsv.iloc[1:,0]],
                         'NAME' : tractcsv.iloc[1:,1],
                         'Population': pd.to_numeric(tractcsv.iloc[1:,2]),
                         'Margin of Error': pd.to_numeric(tractcsv.iloc[1:,3], errors='coerce'),
                         })
# remove Wisconsin state
tractpop = tractpop[tractpop.GEOID!='55']

# set GEOID as index
tractpop = tractpop.set_index('GEOID')

# plot distribution of tract populations
# tractpop.sort_values('Population').reset_index(drop=True).plot(y='Population')

#%% Geography work

# WI DNR shapefile - doesn't have lake winnebago either, so never mind
# shapefile = 'data\\geo\\WI_County_Boundaries_24K.shp'
# countiesWI = gpd.read_file(shapefile)
# countiesWI['NAME'] = countiesWI.COUNTY_NAM

# shapefile of US census tracts in WI
shapefile = 'data\\geo\\cb_2019_55_tract_500k.shp'

# read data set of all WI tracts
witracts = gpd.read_file(shapefile)

# filter on Milwaukee county
mketracts = witracts[witracts.COUNTYFP=='079']

# set GEOID as index
mketracts = mketracts.set_index('GEOID')

# now that both have same index, get population from tractpop
mketracts['Population'] = tractpop['Population']

#%% Select dates of interest
latest_date = covid_tract.Date.max()

delta = 28
delta_str = '(' + str(delta) + ' days)'

# start_date = datetime.datetime(year=2020, month=4, day=11)  # earliest date of tract tracking
# end_date = start_date + datetime.timedelta(days=28)

deltas = list()
start_dates = list()
end_dates = list()

# start_dates.append(datetime.datetime(year=2020, month=1, day=1))
# end_dates.append(datetime.datetime(year=2020, month=5, day=11))
# deltas.append('(as of 11-May)')

# start_dates.append(datetime.datetime(year=2020, month=5, day=11))
# end_dates.append(datetime.datetime(year=2020, month=7, day=15))
# deltas.append('(11-May through 15-July)')

# start_dates.append(datetime.datetime(year=2020, month=7, day=15))
# end_dates.append(datetime.datetime(year=2020, month=9, day=7))
# deltas.append('(15-July through 7-Sep)')

# start_dates.append(datetime.datetime(year=2020, month=9, day=7))
# end_dates.append(datetime.datetime(year=2020, month=10, day=15))
# deltas.append('(8-Sep through 15-Oct)')

# start_dates.append(datetime.datetime(year=2020, month=10, day=15))
# end_dates.append(datetime.datetime(year=2020, month=11, day=23))
# deltas.append('(16-Oct through 23-Nov)')

start_dates.append(datetime.datetime(year=2020, month=1, day=1))
end_dates.append(datetime.datetime(year=2020, month=11, day=23))
deltas.append('(Total)')




for dd, delta_str in enumerate(deltas):
    
    #%% Filter covid data on Milwaukee and on desired dates
    start_date = start_dates[dd]
    end_date = end_dates[dd]
    
    
    # total - from latest date
    total = covid_tract_mke[covid_tract_mke.Date==latest_date]
    total = total.set_index('GEOID')
        
    # only keep columns you can do math on
    col_list = ['POSITIVE', 'NEGATIVE', 'HOSP_YES', 'DEATHS']

    total_end = covid_tract_mke.loc[covid_tract_mke.Date == end_date]
    total_end = total_end.set_index('GEOID')[col_list]
        
    if start_date > datetime.datetime(year=2020, month=4, day=11):
        total_start = covid_tract_mke.loc[covid_tract_mke.Date == start_date]
        total_start = total_start.set_index('GEOID')[col_list]
        timeperiod = total_end - total_start
    else:
        timeperiod = total_end 
    
    
    # get rid of negative values - weird that this is needed
    timeperiod.POSITIVE = (timeperiod.POSITIVE >=0) * timeperiod.POSITIVE
    timeperiod.HOSP_YES = (timeperiod.HOSP_YES >=0) * timeperiod.HOSP_YES
    
    mketracts['Tested (Total)'] = total['POSITIVE'] + total['NEGATIVE']
    mketracts['Cases (Total)'] = total['POSITIVE']
    mketracts['Hosp (Total)'] = total['HOSP_YES']
    mketracts['Deaths (Total)'] = total['DEATHS']
    mketracts['Tested '+delta_str] = timeperiod['POSITIVE'] + timeperiod['NEGATIVE']
    mketracts['Cases '+delta_str] = timeperiod['POSITIVE']
    mketracts['Hosp '+delta_str] = timeperiod['HOSP_YES']
    mketracts['Deaths '+delta_str] = timeperiod['DEATHS']
    mketracts['Tested per 1K (Total)'] = mketracts['Tested (Total)'] / mketracts['Population'] * 1000
    mketracts['Cases per 1K (Total)'] = mketracts['Cases (Total)'] / mketracts['Population'] * 1000
    mketracts['Hosp per 1K (Total)'] = mketracts['Hosp (Total)'] / mketracts['Population'] * 1000
    mketracts['Tested per 1K '+delta_str] = mketracts['Tested '+delta_str] / mketracts['Population'] * 1000
    mketracts['Cases per 1K '+delta_str] = mketracts['Cases '+delta_str] / mketracts['Population'] * 1000
    mketracts['Hosp per 1K '+delta_str] = mketracts['Hosp '+delta_str] / mketracts['Population'] * 1000
    
    
    # fill nan
    mketracts.fillna(0, inplace=True)
    
    # # chloropleths by population, cases, hosp, deaths
    # mketracts.plot(column='Population', edgecolor='w', linewidth=0.5, legend=True)
    # mketracts.plot(column='Total Cases', edgecolor='w', linewidth=0.5, legend=True, cmap='Blues')
    # mketracts.plot(column='Cases per 10K', edgecolor='w', linewidth=0.5, legend=True, cmap='Blues')
    # mketracts.plot(column='Total Hosp', edgecolor='w', linewidth=0.5, legend=True, cmap='Oranges')
    # mketracts.plot(column='Hosp per 10K', edgecolor='w', linewidth=0.5, legend=True, cmap='Oranges')
    # mketracts.plot(column='Total Deaths', edgecolor='w', linewidth=0.5, legend=True, cmap='Reds')
    
    # deaths by tract do not sum up to the state deaths, less than half accounted for.
    # positives and negatives do.
    # HOSP_YES is close but about 10% off.
    
    



    #%% Color-bubble maps
    
    fig_height = 700
    
    tract_names = ['Tract ' + n[5:] for n in mketracts.index]
    
    
    
    #%% Plots for total
    select_str = delta_str
    # adjust factor lower for larger bubbles, max lower for more colorful bubbles
    cases_size_factor = 2
    cases_color_max = 120
    
    # #%% Plots for timeperiod
    # select_str = delta_str
    # cases_size_factor = 0.8
    # cases_color_max = 40
    
    
    #%% Ranges for hosp and tests plots
    cases_color_range = [0, cases_color_max]
    hosp_size_factor = cases_size_factor * 0.08   # so that bubbles are same size if hosp = 8% of cases 
    hosp_color_range = [0, cases_color_max*0.08]
    tested_size_factor = cases_size_factor / 0.15 # so that bubbles are the same size if cases = 15% of tested
    tested_color_range = [0, cases_color_max/0.15]


    #%% Color-bubble plots


        
    # Cases color-bubble
    
    fig = covid.plotly_colorbubble(
        mketracts,
        sizecol='Cases '+select_str,
        colorcol='Cases per 1K '+select_str,
        size_factor=cases_size_factor,
        color_range=cases_color_range,
        colorscale='Blues',
        location_names=tract_names,
        plotlabels=dict(
            title='Milwaukee: Cases by Census Tract<br>'+select_str,
            sizelabel='Number of cases',
            colorlabel='Cases per 1K',
            ),
        savefile='.\\docs\\assets\\plotly\\Map-Cases-Milwaukee.html',
        fig_height=fig_height,
        )
    
    fig.write_image(
        '.\\docs\\assets\\Map-Cases-Milwaukee-Total_2020-11-27.png',
        width=700,
        height=700,
        engine='kaleido',
    )
    
    # Tests color-bubble
    fig = covid.plotly_colorbubble(
        mketracts,
        sizecol='Tested '+select_str,
        colorcol='Tested per 1K '+select_str,
        size_factor=tested_size_factor,
        color_range=tested_color_range,
        colorscale='Greens',
        location_names=tract_names,
        plotlabels=dict(
            title='Milwaukee: Tests by Census Tract<br>'+select_str,
            sizelabel='Number tested',
            colorlabel='Tested per 1K',
            ),
        savefile='.\\docs\\assets\\plotly\\Map-Tested-Milwaukee.html',
        fig_height=fig_height,
        )
    
    fig.write_image(
        '.\\docs\\assets\\Map-Tested-Milwaukee-Total_2020-11-27.png',
        width=700,
        height=700,
        engine='kaleido',
    )
    
    # Hospitalizations color-bubble
    fig = covid.plotly_colorbubble(
        mketracts,
        sizecol='Hosp '+select_str,
        colorcol='Hosp per 1K '+select_str,
        size_factor=hosp_size_factor,
        color_range=hosp_color_range,
        colorscale='Oranges',
        location_names=tract_names,
        plotlabels=dict(
            title='Milwaukee: Hospitalizations by Census Tract<br>'+select_str,
            sizelabel='Number of hosp',
            colorlabel='Hosp per 1K',
            ),
        savefile='.\\docs\\assets\\plotly\\Map-Hosp-Milwaukee.html',
        fig_height=fig_height,
        )
    
    fig.write_image(
        '.\\docs\\assets\\Map-Hosp-Milwaukee-Total_2020-11-27.png',
        width=700,
        height=700,
        engine='kaleido',
    )
