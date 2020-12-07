# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 09:03:15 2020

@author: Matt Bayer
"""



import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

import covid

#%% Load data

state = covid.read_covid_data_wi('state')

covid.plot_by_age(state)

# rename
col_rename = {'Date': 'Date', 'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
state = state.rename(columns=col_rename)




#%% Plot deaths vs cases
# contra Trevor Bedford on the national data - this seems to fit better with a 
# deaths delay of 12 days (instead of 21) and a CFR of 1.0% (instead of 1.8%).

delay = 12   # days
delay_str = 'Deaths (-'+str(delay)+' days)'

# create delayed death column
deaths = state[['Date', 'Deaths']]
deaths.Date = deaths.Date - datetime.timedelta(days=delay)
deaths = deaths.set_index('Date')
state = state.set_index('Date')
state[delay_str] = deaths
state = state.reset_index()



#%% Plot all cases vs. deaths
CFR = 1.0

savefile = '.\\docs\\assets\\plotly\\Cases-Deaths-WI.html'

fig = covid.plotly_twolines(
    state,
    delay_str,
    'Cases',
    plotcolors=['firebrick', 'steelblue', 'rosybrown'],
    secondary_scale=1/(CFR/100),
    plotlabels = {'title': 'WI Deaths and Cases<br>(assuming CFR '+str(CFR)+'%)',
                  'yaxis': 'Deaths',
                  'yaxis_secondary': 'Cases',
                  },
    column1_bar=True,
    savefile=savefile,
    )    

# save_png = '.\\docs\\assets\\Cases-Deaths-WI_2020-12-06.png'
save_png = '.\\docs\\assets\\Cases-Deaths-WI.png'
fig.write_image(
    save_png,
    width=900,
    height=600,
    engine='kaleido',
)
os.startfile(save_png)


