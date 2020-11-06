# -*- coding: utf-8 -*-
"""
Create interactive maps for cases and hospitalizations using Plotly.
"""

import pandas as pd
import geopandas as gpd

import covid

#%% Get the coviddata
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'
csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
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
select = select[select.Date==latest_date]
select = select.set_index('GEOID')

mketracts['Total Deaths'] = select['DEATHS']
mketracts['Total Hosp'] = select['HOSP_YES']
mketracts['Total Cases'] = select['POSITIVE']
mketracts['Cases per 10K'] = mketracts['Total Cases'] / mketracts['Population'] * 10000
mketracts['Hosp per 10K'] = mketracts['Total Hosp'] / mketracts['Population'] * 10000


# fill nan
mketracts.fillna(0, inplace=True)

# mketracts = mketracts.assign(Deaths=mketracts.GEOID.apply(lambda id: select.loc[id,'DEATHS']))
# mketracts = mketracts.assign(Cases=mketracts.GEOID.apply(lambda id: select.loc[id,'POSITIVE']))
# mketracts = mketracts.assign(Hosp=mketracts.GEOID.apply(lambda id: select.loc[id,'HOSP_YES']))

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




#%%
if False:
    
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
    countiesWI['Cases per 100,000'] = countiesWI['Cases'] / countiesWI['Population'] * 100000
    
    # hospitalizations
    hosp = reduced.pivot(index='Date', columns='County', values='Hospitalizations')
    hosp_avg = hosp.rolling(window=avg_window, center=False).mean()
    hosp_for_map = hosp_avg.iloc[-1]
    
    countiesWI['Hospitalizations'] = hosp_for_map
    countiesWI['Hospitalizations per 100,000'] = countiesWI['Hospitalizations'] / countiesWI['Population'] * 100000
    




#%% Color-bubble maps

cases_size_factor = 0.6
cases_color_max = 600
cases_color_range = [0, cases_color_max]
hosp_size_factor = cases_size_factor * .05   # so that bubbles are same size if hosp = 5% of cases 
hosp_color_range = [0, cases_color_max*.05]

tract_names = ['Tract ' + n[5:] for n in mketracts.index]

# Cases color-bubble
covid.plotly_colorbubble(
    mketracts,
    sizecol='Total Cases',
    colorcol='Cases per 10K',
    size_factor=cases_size_factor,
    color_range=cases_color_range,
    colorscale='Blues',
    location_names=tract_names,
    savefile='.\\docs\\assets\\plotly\\Map-Cases-Milwaukee1.html',
    plotlabels=dict(title='Milwaukee: Cases by Census Tract<br>(Total)'),
    )


#%% Hospitalizations color-bubble
covid.plotly_colorbubble(
    mketracts,
    sizecol='Total Hosp',
    colorcol='Hosp per 10K',
    size_factor=hosp_size_factor,
    color_range=hosp_color_range,
    colorscale='Oranges',
    location_names=tract_names,
    savefile='.\\docs\\assets\\plotly\\Map-Hosp-Milwaukee1.html',
    plotlabels=dict(title='Milwaukee: Hospitalizations by Census Tract<br>(Total)'),
    )
