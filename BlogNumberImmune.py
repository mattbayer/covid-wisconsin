# -*- coding: utf-8 -*-
"""
Estimate the total number of people immune.

Created on Thu May 20 12:58:30 2021

@author: 212367548
"""

import covid

import pandas as pd
import numpy as np
import plotly.express as px
import os

from tableauscraper import TableauScraper as TS


#%% Helper functions
def loads_with_retries(ts, url, retries):
    for attempt in range(retries):
        try:
            ts.loads(url)
        except Exception as e:
            err = e
            print('Retrying TS load...')
        else:
            break
    else:
        raise err    
    return ts

#%% Get cases by age group
# Pull from tableau instead of downloadable data, because the tableau plot has
# the right age groups to match up with vaccinations.

url = 'https://bi.wisconsin.gov/t/DHS/views/Agegroupovertime/Cases?:embed_code_version=3&:embed=y&:loadOrderID=3&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'

ts = TS()       
ts = loads_with_retries(ts, url, 3)

age_dash = ts.getWorkbook()

age_total = age_dash.worksheets[0].data

col_rename = {'New Age Groups-alias': 'Age group',
              'CNTD(Incident ID)-alias': 'Cases',
              'SUM(case rate by age for 100K )-alias': 'Cases per 100K',
              'WEEK(Episode Date Trunc)-value': 'Week of'}

age_total = age_total[col_rename.keys()]
age_total = age_total.rename(columns=col_rename)
age_total['Week of'] = pd.to_datetime(age_total['Week of'])

# only need the most recent cumulative number
age_total = age_total[age_total['Week of'] == age_total['Week of'].max()]

# set age group to index
age_total = age_total.set_index('Age group')


#%% Get vax by age group from WI DHS data

vax_age_file = 'data\\vaccinations\\Vax-Age-WI.csv'
vax_age = pd.read_csv(vax_age_file, converters={'Reporting date': pd.to_datetime})

# trim to most recent numbers
vax_age = vax_age[vax_age['Reporting date'] == vax_age['Reporting date'].max()]
vax_age = vax_age.drop('Reporting date', axis=1)

# set age group to index
vax_age = vax_age.set_index('Age group')

#%% Get overall vax data from CDC

# from Our World In Data github, recording CDC data

vax_github = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv'
vax_cdc = pd.read_csv(vax_github, converters={'date': pd.to_datetime})

# vax_offline = 'data/vaccinations/us_state_vaccinations.csv'
# vax_df = pd.read_csv(vax_offline, converters={'date': pd.to_datetime})

vax_cdc = vax_cdc[vax_cdc.location == 'Wisconsin']
vax_cdc = vax_cdc[vax_cdc.date == vax_cdc.date.max()]



#%% Do estimates
# Note that populations for vax and cases differ by up to ~3.5%
infection_factor = 3

# derived and estimates
age_total['Population'] = age_total['Cases'] / age_total['Cases per 100K'] * 1e5
age_total['Est Infected %'] = age_total['Cases per 100K'] / 1000 * infection_factor

# create <18 index for vax_age
vax_age['Population'] = vax_age['Initiated #'] / vax_age['Initiated %']
vax_age.loc['<18'] = [np.nan]*5
vax_age.loc['<18','Initiated #'] = vax_age.loc['16-17':'12-15','Initiated #'].sum()
vax_age.loc['<18','Completed #'] = vax_age.loc['16-17':'12-15','Completed #'].sum()
# no need for other columns at the moment

# add initiated # to age_total
age_total['Vaccinated #'] = vax_age['Initiated #']
age_total['Vaccinated %'] = age_total['Vaccinated #'] / age_total['Population'] * 100

# Increase in estimate from CDC data
cdc_factor = vax_cdc.people_vaccinated / age_total['Vaccinated #'].sum()


# Estimate total immunity by age group
age_total['Immune %'] = age_total['Vaccinated %'] + (100-age_total['Vaccinated %']) * age_total['Est Infected %']/100

#%% Estimate total 


wi_pop = age_total['Population'].sum()
total_immune_age = (age_total['Immune %'] / 100 * age_total['Population']).sum() / wi_pop

total_vax = age_total['Vaccinated #'].sum() / wi_pop
total_infected = age_total['Cases'].sum() * infection_factor / wi_pop
total_immune_naive = total_vax + (1-total_vax) * total_infected


#%% Trying by county?

county = covid.read_covid_data_wi('county')
county = county[county.Date==pd.to_datetime('2021-05-20')]
county = county.set_index('NAME')

# population data
popdata = covid.read_pop_data_wi('data\\Population-Data-WI.csv')

county['Population'] = popdata

# vax data
url = 'https://bi.wisconsin.gov/t/DHS/views/VaccinesAdministeredtoWIResidents_16212677845310/VaccinatedWisconsin-County?:embed_code_version=3&:embed=y&:loadOrderID=1&:display_spinner=no&:showAppBanner=false&:display_count=n&:showVizHome=n&:origin=viz_share_link'
ts = loads_with_retries(ts, url, 3)
vax_dash = ts.getWorkbook()
vax_county = vax_dash.worksheets[0].data

col_rename = {'Region-alias': 'Region',
              'County-alias': 'County',
              'Measure Names-alias': 'Measure',
              'Measure Values-alias': 'Value'}

vax_county = vax_county[col_rename.keys()]
vax_county = vax_county.rename(columns=col_rename)

# remove 'County' from the end of every county name
vax_county.County.apply(lambda s: s.replace())

# update_date = format_date(allocation_dash.worksheets[2].data.iloc[0,2])
