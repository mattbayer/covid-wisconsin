# -*- coding: utf-8 -*-
"""
Work with Covid Tracking Project data.

Created on Thu Jan  7 15:18:34 2021

@author: 212367548
"""

import pandas as pd
import covid
import plotly.express as px
from plotly.offline import plot as pplot

#%% fetch data for wisconsin
state = 'wi'

url_state = 'https://api.covidtracking.com/v1/states/'+state+'/daily.csv'
url_all = 'https://api.covidtracking.com/v1/states/daily.csv'

state = pd.read_csv(url_state)

usa = pd.read_csv(url_all)

# convert dates
state['Date'] = pd.to_datetime(state['date'], format='%Y%m%d')
usa['Date'] = pd.to_datetime(usa['date'], format='%Y%m%d')

#%% Plot cases against total tests
# remember total tests only fully populated oct 29... doesn't seem to have
# caused a discontinuity though


# Cases / Tests line plot
covid.plotly_casetest(sourcedata=state, 
                      case_col='positiveIncrease', 
                      test_col='totalTestResultsIncrease', 
                      date_col='Date', 
                      savefile='docs\\assets\\plotly\\Cases-Tests-WI-CTP.html',
                      )

#%% Plot WI vs. MN

compare = usa.loc[usa.state.apply(lambda s: s in ['WI', 'MN'])]

fig = px.line(compare, x='Date', y='totalTestResultsIncrease', color='state')

pplot(fig, 
      filename='.\\docs\\assets\\plotly\\WI-MN.html',
      include_plotlyjs='cdn',
      )