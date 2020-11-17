# -*- coding: utf-8 -*-
"""
Create interactive maps for cases and hospitalizations using Plotly.
"""

import pandas as pd
import geopandas as gpd
import datetime

import covid

import re

#%%

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
covid.update_covid_data_wi('tract')
tract = covid.read_covid_data_wi('tract')


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

#%%

# add deaths as a column
latest_date = tract.Date.max()
select = tract[tract.GEO=='Census tract']

total = select[select.Date==latest_date]
total = total.set_index('GEOID')

delta = 14
total_delta = select[select.Date==(latest_date - datetime.timedelta(days=delta))]
total_delta = total_delta.set_index('GEOID')

col_list = ['POSITIVE', 'NEGATIVE', 'HOSP_YES', 'DEATHS']
recent = total[col_list]
recent = recent - total_delta[col_list]
# get rid of negative values - weird that this is needed
recent.POSITIVE = (recent.POSITIVE >=0) * recent.POSITIVE
recent.HOSP_YES = (recent.HOSP_YES >=0) * recent.HOSP_YES

mketracts['Total Tested'] = total['POSITIVE'] + total['NEGATIVE']
mketracts['Total Cases'] = total['POSITIVE']
mketracts['Total Hosp'] = total['HOSP_YES']
mketracts['Total Deaths'] = total['DEATHS']
mketracts['Tested (14 days)'] = recent['POSITIVE'] + recent['NEGATIVE']
mketracts['Cases (14 days)'] = recent['POSITIVE']
mketracts['Hosp (14 days)'] = recent['HOSP_YES']
mketracts['Deaths (14 days)'] = recent['DEATHS']
mketracts['Tested per 10K'] = mketracts['Total Tested'] / mketracts['Population'] * 10000
mketracts['Cases per 10K'] = mketracts['Total Cases'] / mketracts['Population'] * 10000
mketracts['Hosp per 10K'] = mketracts['Total Hosp'] / mketracts['Population'] * 10000
mketracts['Tested per 10K (14 days)'] = mketracts['Tested (14 days)'] / mketracts['Population'] * 10000
mketracts['Cases per 10K (14 days)'] = mketracts['Cases (14 days)'] / mketracts['Population'] * 10000
mketracts['Hosp per 10K (14 days)'] = mketracts['Hosp (14 days)'] / mketracts['Population'] * 10000


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

# adjust factor lower for larger bubbles, max lower for more colorful bubbles
# cases_size_factor = 0.8
# cases_color_max = 800
cases_size_factor = 0.4
cases_color_max = 150
cases_color_range = [0, cases_color_max]
hosp_size_factor = cases_size_factor * .05   # so that bubbles are same size if hosp = 5% of cases 
hosp_color_range = [0, cases_color_max*.05]
tested_size_factor = cases_size_factor * 5 # so that bubbles are the same size if cases = 20% of tested
tested_color_range = [0, cases_color_max*5]

tract_names = ['Tract ' + n[5:] for n in mketracts.index]

#%% Cases color-bubble
covid.plotly_colorbubble(
    mketracts,
    # sizecol='Total Cases',
    # colorcol='Cases per 10K',
    sizecol='Cases (14 days)',
    colorcol='Cases per 10K (14 days)',
    size_factor=cases_size_factor,
    color_range=cases_color_range,
    colorscale='Blues',
    location_names=tract_names,
    savefile='.\\docs\\assets\\plotly\\Map-Cases-Milwaukee.html',
    plotlabels=dict(title='Milwaukee: Cases by Census Tract<br>(14 days)'),
    )

#%% Tests color-bubble
covid.plotly_colorbubble(
    mketracts,
    # sizecol='Total Cases',
    # colorcol='Cases per 10K',
    sizecol='Tested (14 days)',
    colorcol='Tested per 10K (14 days)',
    size_factor=tested_size_factor,
    color_range=tested_color_range,
    colorscale='Greens',
    location_names=tract_names,
    savefile='.\\docs\\assets\\plotly\\Map-Tested-Milwaukee.html',
    plotlabels=dict(title='Milwaukee: Tests by Census Tract<br>(14 days)'),
    )

#%% Hospitalizations color-bubble
covid.plotly_colorbubble(
    mketracts,
    # sizecol='Total Hosp',
    # colorcol='Hosp per 10K',
    sizecol='Hosp (14 days)',
    colorcol='Hosp per 10K (14 days)',
    size_factor=hosp_size_factor,
    color_range=hosp_color_range,
    colorscale='Oranges',
    location_names=tract_names,
    savefile='.\\docs\\assets\\plotly\\Map-Hosp-Milwaukee.html',
    plotlabels=dict(title='Milwaukee: Hospitalizations by Census Tract<br>(14 days)'),
    )
