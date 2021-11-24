# -*- coding: utf-8 -*-
"""
Update data from WI DHS automatically using Github Actions.

Created on Thu Dec 24 12:33:03 2020

@author: Matt Bayer
"""

import covid
import datetime

try:
    #%% Update data
    covid.update_covid_data_wi('state')
    covid.update_covid_data_wi('county')
    
    state = covid.read_covid_data_wi('state')
    
    
    #%% Dashboard - state line plots
    plotpath = '.\\docs\\_includes\\plotly'
    
    # reduce and rename at state level
    col_rename = {'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
    state = state.rename(columns=col_rename)
    
    # Cases / Tests line plot
    covid.plotly_casetest(sourcedata=state, 
                          case_col='Cases', 
                          test_col='Tests', 
                          date_col='Date', 
                          savefile=plotpath + '\\Cases-Tests-WI.html',
                          date_min=datetime.datetime(2021,1,15),
                          range_max=2000,
                          showfig=False,
                          )
    
    # Deaths / Hospitalizations line plot
    covid.plotly_deadhosp(sourcedata=state, 
                          hosp_col='Hospitalizations', 
                          dead_col='Deaths', 
                          date_col='Date', 
                          savefile=plotpath + '\\Deaths-Hosp-WI.html',
                          date_min=datetime.datetime(2021,1,15),
                          range_max=100,
                          showfig=False,
                          )
except:
    print("Update Legacy Data / Plots error")

#%% Dashboard - monitoring plots

try:
    import UpdateMonitoringPlots
except:
    print("UpdateMonitoringPlots error")

try:
    import UpdateRegionalPositivity
except:
    print("UpdateRegionalPositivity error")

#%% Dashboard - outcomes plots
try:
    import UpdateOutcomePlots
except:
    print("UpdateOutcomePlots error")

#%% Dashboard - other plots

try:
    import UpdateGeo
except:
    print("UpdateGeo error")
        
try:
    import UpdateRegional
except:
    print("UpdateRegional error")
