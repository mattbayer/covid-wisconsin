# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 20:42:39 2021

@author: matt_
"""

import pandas as pd
import covid


# Previous attempt at all HHS data, to sort later
# - json version could not report more than 1000 data rows
# hhsdata2 = pd.read_csv('https://healthdata.gov/api/views/g62h-syeh/rows.csv?accessType=DOWNLOAD&api_foundry=true')
# hhsdata = pd.read_json(hhsdata_url)
# widata = hhsdata[hhsdata.state=='WI']

# https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh

# can directly filter on WI in API call to reduce data
hhs_wi_url = 'https://healthdata.gov/resource/g62h-syeh.json?state=WI'

widata = pd.read_json(hhs_wi_url)


# convert and sort by date
widata.date = pd.to_datetime(widata.date.copy())
widata = widata.sort_values('date')

# various random plots
widata.plot(x='date', y=['previous_day_admission_adult_covid_confirmed', 'previous_day_admission_adult_covid_suspected'])

widata.plot(x='date', y=['inpatient_beds_used_covid', 'total_adult_patients_hospitalized_confirmed_covid'])

widata.plot(x='date', y=['previous_day_admission_pediatric_covid_confirmed', 'previous_day_admission_pediatric_covid_suspected'])
widata.plot(x='date', y=['previous_day_admission_pediatric_covid_suspected', 'previous_day_admission_pediatric_covid_suspected_coverage'])


widata.plot(x='date', y=['total_pediatric_patients_hospitalized_confirmed_covid'])


# Big question - numbers seem 50-100% higher than state data. Why?


#%%
statedata = covid.download_covid_data_wi('state2')

#%%
def clean_state2(state):
    col_rename = {'POS_NEW_CONF': 'Cases',
                  'DTH_CONF_Daily': 'Deaths',
                  'TESTS_NEW': 'Tests',
                  'Date': 'Date',
                  }
    state = state[col_rename.keys()]
    state = state.rename(columns=col_rename)
    # convert to date object and discard time portion
    state.Date = pd.to_datetime(state.Date).apply(lambda d: d.date())
    return state
    
state = clean_state2(statedata)

# add hospital admissions to state data
state = state.set_index('Date')
state['Admissions'] = widata.set_index('date')['previous_day_admission_adult_covid_confirmed']
state = state.reset_index()

#%% Plots with mix and match data
plotpath = '.\\docs\\assets\\plotly'

covid.plotly_deadhosp(sourcedata=state, 
                      hosp_col='Admissions', 
                      dead_col='Deaths', 
                      date_col='Date', 
                      savefile=plotpath + '\\Deaths-Hosp-WI-HHS.html',
                      # date_min=datetime.datetime(2021,1,15),
                      range_max=100,
                      showfig=True,
                      )
