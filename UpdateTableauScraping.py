# -*- coding: utf-8 -*-
"""
Update data files scraped from Tableau dashboards on the DHS website

Uses TableauScraper, https://github.com/bertrandmartel/tableau-scraping

Designed to be run with Github Actions.

Created on Tue Apr 27 09:22:05 2021

@author: 212367548
"""


import pandas as pd
import pickle

from tableauscraper import TableauScraper as TS

#%% Helper functions

def format_date(date_str):
    return pd.to_datetime(date_str).strftime('%Y-%m-%d')

def update_file(filename, update, on):
    # load file of previous data
    compiled = pd.read_csv(filename)
        
    # first update any overlapping data
    # set indices to the "on" columns, for both previous and updated data
    compiled = compiled.set_index(on)
    update = update.set_index(on)
    compiled.update(update)
    
    # then reset indices and do a merge to add new data
    compiled = compiled.reset_index()
    update = update.reset_index()
    compiled = pd.merge(compiled, update, how='outer')
        
    # save updated file
    compiled.to_csv(filename, index=False)   

#%% vaccine allocation

url = 'https://bi.wisconsin.gov/t/DHS/views/VaccineDistribution/Allocated?:embed_code_version=3&:embed=y&:loadOrderID=0&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'


ts = TS()
ts.loads(url)
allocation_dash = ts.getWorkbook()

#%% 
# Vaccine by county and age
url = 'https://bi.wisconsin.gov/t/DHS/views/VaccinesAdministeredtoWIResidents_16129838459350/VaccinatedWisconsin-County?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
ts.loads(url)
vax_dash = ts.getWorkbook()
vax_complete = vax_dash.setParameter('Initiation or Completion', 'Residents who have completed the vaccine series')


update_date = format_date(allocation_dash.worksheets[2].data.iloc[0,2])


datafile = 'data\\vaccinations\\vax-dashboards_'+update_date+'.pkl'
with open(datafile, 'wb') as f:
    pickle.dump([allocation_dash, vax_dash, vax_complete], f)
    
    
#%% manufacturer counts
manufacturer = allocation_dash.worksheets[1].data
col_rename = {'Trade Name-value': 'Trade Name',
              'SUM(Immunization Count)-alias': 'Count'}
manufacturer = manufacturer[col_rename.keys()]
manufacturer = manufacturer.rename(columns=col_rename)
manufacturer.Count = pd.to_numeric(manufacturer.Count.copy())
manufacturer = manufacturer.set_index('Trade Name').T

# Will not necessarily match the sum of all the trade names
manufacturer['All'] = allocation_dash.worksheets[2].data.iloc[0,1]
# manufacturer.insert(0, 'Reporting date', pd.to_datetime(allocation_dash.worksheets[2].data.iloc[0,2]))
manufacturer.insert(0, 'Reporting date', allocation_dash.worksheets[2].data.iloc[0,2])

# Rename stuff
manufacturer = manufacturer.reset_index(drop=True)
manufacturer.columns.name = ''

#%% Update manufacturer file

man_file = 'data\\vaccinations\\Vax-Manuf-WI.csv'

update_file(man_file, manufacturer, on='Reporting date')



#%% Extract data for vaccines by age group

col_rename = {'Age-value': 'Age group',
              'SUM(Initiation or completed count for TT)-alias': 'Initiated #',
              'AGG(Calc- Initiation or Full Coverage)-alias': 'Initiated %'
              }

# vax_age = vax_dash.worksheets[1].data[col_rename.keys()]
# get worksheet by name instead of index, index seems to be unstable
vax_age = vax_dash.getWorksheet('Age vax/unvax County').data[col_rename.keys()]
vax_age = vax_age.rename(columns=col_rename)

col_rename = {'Age-value': 'Age group',
              'SUM(Initiation or completed count for TT)-alias': 'Completed #',
              'AGG(Calc- Initiation or Full Coverage)-alias': 'Completed %'
              }

# vax_age_complete = vax_complete.worksheets[8].data[col_rename.keys()]
# get worksheet by name instead of index, index seems to be unstable
vax_age_complete = vax_complete.getWorksheet('Age vax/unvax County').data[col_rename.keys()]
vax_age_complete = vax_age_complete.rename(columns=col_rename)

# merge the initiated and completed data
vax_age = vax_age.merge(vax_age_complete)

# add date
vax_age.insert(0, 'Reporting date', vax_dash.worksheets[14].data.iloc[0,0])


#%% Update age group file

vax_age_file = 'data\\vaccinations\\Vax-Age-WI.csv'

update_file(vax_age_file, vax_age, on=['Reporting date', 'Age group'])

#%% Extract data for vaccines by race & ethnicity

# first doses ----

race_rename = {'Race-alias': 'Race',
               'SUM(Initiation or completed count for TT)-alias': 'Initiated #',
               'AGG(Calc- Initiation or Full Coverage)-alias': 'Initiated %'
               }
ethn_rename = {'Ethnicity-value': 'Ethnicity',
               'SUM(Initiation or completed count for TT)-alias': 'Initiated #',
               'AGG(Calc- Initiation or Full Coverage)-alias': 'Initiated %'
               }

# get worksheets by name
vax_race = vax_dash.getWorksheet('Race vax/unvax county').data[race_rename.keys()]
vax_ethn = vax_dash.getWorksheet('Ethnicity vax/unvax county').data[ethn_rename.keys()]

# rename columns
vax_race = vax_race.rename(columns=race_rename)
vax_ethn = vax_ethn.rename(columns=ethn_rename)

# second doses ----

race_rename = {'Race-alias': 'Race',
               'SUM(Initiation or completed count for TT)-alias': 'Completed #',
               'AGG(Calc- Initiation or Full Coverage)-alias': 'Completed %'
               }
ethn_rename = {'Ethnicity-value': 'Ethnicity',
               'SUM(Initiation or completed count for TT)-alias': 'Completed #',
               'AGG(Calc- Initiation or Full Coverage)-alias': 'Completed %'
               }

vax_race_complete = vax_complete.getWorksheet('Race vax/unvax county').data[race_rename.keys()]
vax_ethn_complete = vax_complete.getWorksheet('Ethnicity vax/unvax county').data[ethn_rename.keys()]
vax_race_complete = vax_race_complete.rename(columns=race_rename)
vax_ethn_complete = vax_ethn_complete.rename(columns=ethn_rename)

# merge the initiated and completed data
vax_race = vax_race.merge(vax_race_complete)
vax_ethn = vax_ethn.merge(vax_ethn_complete)

# add date
repdate = vax_dash.worksheets[14].data.iloc[0,0]
vax_race.insert(0, 'Reporting date', repdate)
vax_ethn.insert(0, 'Reporting date', repdate)

#%% Update race/ethnicity files

vax_race_file = 'data\\vaccinations\\Vax-Race-WI.csv'
vax_ethn_file = 'data\\vaccinations\\Vax-Ethnicity-WI.csv'

update_file(vax_race_file, vax_race, on=['Reporting date', 'Race'])
update_file(vax_ethn_file, vax_ethn, on=['Reporting date', 'Ethnicity'])

#%% Get deaths by date of death

cdeath_url = 'https://bi.wisconsin.gov/t/DHS/views/County-leveldailydeathsconfirmedandprobable/Stackeddeathsbyday?:embed_code_version=3&:embed=y&:loadOrderID=3&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'

ts.loads(cdeath_url)
cdeath_dash = ts.getWorkbook()

update_date = format_date(cdeath_dash.worksheets[0].data.iloc[0,-1])

death_data = cdeath_dash.worksheets[1].data
death_file = 'data\\Deaths by day auto_' + update_date + '.csv'
death_data.to_csv(death_file)