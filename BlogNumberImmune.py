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
age_total['Vax+Inf %'] = age_total['Vaccinated %'] * age_total['Est Infected %']/100
age_total['Vax only %'] = age_total['Vaccinated %'] - age_total['Vax+Inf %']
age_total['Inf only %'] = (100-age_total['Vaccinated %']) * age_total['Est Infected %']/100
age_total['Immune %'] = age_total['Vaccinated %'] + age_total['Inf only %']


#%% Bar plots for age groups


# perc_cols = ['Vaccinated %','Immune %', 'Est Infected %']
# perc_cols = ['Vaccinated %', 'Est Infected %', 'Immune %']
perc_cols = ['Vax only %', 'Vax+Inf %', 'Inf only %']
col_colors = ['seagreen', 'darkslategray', 'steelblue']

# reformat to "long" for use in the bar graph
age_total = age_total.reindex(['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+'])
age_long = age_total.reset_index().melt(id_vars='Age group', value_vars=perc_cols, value_name='Percentage')

# create text labels - strings from rounding each percentage value to nearest whole
def perc_to_text(p):
    if p < 2:
        t = '{:0.1f}'.format(p) + '%'
    else:
        t = '{:0.0f}'.format(p) + '%'
    return t

age_long['ImmuneLabel'] = ''
age_long.iloc[14:,-1] = age_total['Immune %'].apply(perc_to_text)

# vertical layout
fig = px.bar(
    age_long, 
    x='Age group', 
    y='Percentage', 
    text='ImmuneLabel',
    color='variable',
    color_discrete_sequence=col_colors,
    # barmode='overlay',
    labels={'variable': '', 'Percentage':'Immune %'},
    title='Estimated Immunity by Age Group',
    width=700,
    height=700,
    )


# take out 'variable=' part of the axis titles
fig.for_each_annotation(
    lambda a: a.update(
        text=a.text.split("=")[-1],
        font=dict(size=15),
        )
    )

fig.update_traces(textposition='outside')


# other layout
fig.update_layout(showlegend=True)


#%% Alternative bar plot
perc_cols = ['Vaccinated %', 'Est Infected %']
col_colors = ['seagreen', 'steelblue']

# reformat to "long" for use in the bar graph
age_total = age_total.reindex(['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+'])
age_long = age_total.reset_index().melt(id_vars='Age group', value_vars=perc_cols, value_name='Percentage')

# create text labels - strings from rounding each percentage value to nearest whole
def perc_to_text(p):
    if p < 2:
        t = '{:0.1f}'.format(p) + '%'
    else:
        t = '{:0.0f}'.format(p) + '%'
    return t

age_long['ImmuneLabel'] = ''
age_long.iloc[7:,-1] = age_total['Immune %'].apply(perc_to_text)

# create elevated base for the Infected bar
age_long['Base'] = 0
age_long.iloc[7:,-1] = age_total['Vax only %']

# vertical layout
fig = px.bar(
    age_long, 
    x='Age group', 
    y='Percentage', 
    text='ImmuneLabel',
    color='variable',
    base='Base',
    color_discrete_sequence=col_colors,
    barmode='overlay',
    labels={'variable': '', 'Percentage':'Immune %'},
    title='Estimated Immunity by Age Group',
    width=700,
    height=700,
    )


# take out 'variable=' part of the axis titles
fig.for_each_annotation(
    lambda a: a.update(
        text=a.text.split("=")[-1],
        font=dict(size=15),
        )
    )

fig.update_traces(textposition='outside')


# other layout
fig.update_layout(showlegend=True)


#%% Save and display bar plot

save_html='.\\docs\\assets\\plotly\\Immune-Age.html'
fig.write_html(
    file=save_html,
    default_height=550,
    default_width=700,
    include_plotlyjs='cdn',
)
os.startfile(save_html)

save_png = '.\\docs\\assets\\Immune-Age.png'
fig.write_image(
    save_png,
    width=700,
    height=550,
    engine='kaleido',
)
os.startfile(save_png)




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
# vax_county.County.apply(lambda s: s.replace())

# update_date = format_date(allocation_dash.worksheets[2].data.iloc[0,2])
