# -*- coding: utf-8 -*-
"""
Create interactive line plots using Plotly.
"""

import numpy as np

import plotly
import plotly.express as px
from plotly.offline import plot as pplot
import plotly.graph_objects as go

import covid


#%% Get the data

widata = covid.read_covid_data_wi(dataset='state')


#%% Manipulate data columns for prep

# filter to state
state = widata[widata.NAME == 'WI']
# index and sort by date
state = state.set_index('Date')
state = state.sort_index()

# create new hosp column
state = state.assign(HOSP_NEW = state.HOSP_YES.diff(periods=1))

# reduce and rename columns
col_rename = {'POS_NEW': 'Cases', 'TEST_NEW': 'Tests', 'DTH_NEW': 'Deaths', 'HOSP_NEW': 'Hospitalizations'}
col_cumul = {'POSITIVE': 'Total Cases', 'NEGATIVE': 'Total Negative', 'HOSP_YES': 'Total Hospitalizations', 'DEATHS': 'Total Deaths'}
state = state[col_rename.keys()]
state = state.rename(columns=col_rename)

# rolling 7-day average
state_avg = state.rolling(window=7, center=False).mean()


#%% Standard plots
plotpath = '.\\docs\\assets\\plotly'

# Cases/Tests

# compute y axis range
# want tests to be on a scale exactly 10x cases
range_max = max(state_avg.Tests.max()/10, state_avg.Cases.max())
range_cases = np.array([-range_max * 0.05, 1.05*range_max])


fig = plotly.subplots.make_subplots(specs=[[{"secondary_y": True}]])

# # individual cases bar chart
# fig.add_trace(
#     go.Bar(x=state.index, 
#            y=state.Cases,
#            name='Cases', 
#            marker_color='lightsteelblue', 
#            hovertemplate='%{y:.0f}'),)

# # individual tests bar chart
# fig.add_trace(
#     go.Bar(x=state.index, 
#            y=state.Tests,
#            name='Tests', 
#            marker_color='darkkhaki', 
#            hovertemplate='%{y:.0f}'),
#     secondary_y=True)


fig.add_trace(
    go.Scatter(x=state_avg.index, 
               y=state_avg.Cases, 
               name='Cases (7-day avg)', 
               line_color='steelblue', 
               hovertemplate='%{y:.0f}'),
    secondary_y=False)

fig.add_trace(
    go.Scatter(x=state_avg.index, 
               y=state_avg.Tests, 
               name='Tests (7-day avg)', 
               line_color='olivedrab', #darkolivegreen
               hovertemplate='%{y:.0f}'),
    secondary_y=True)


fig.update_yaxes({'range': range_cases}, secondary_y=False, title_text='Daily cases')
fig.update_yaxes({'range': range_cases*10}, secondary_y=True, title_text='Daily new people tested')
fig.update_layout(title_text='WI Daily Cases and Tests',
                  hovermode='x unified',
                  legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))                
                
# plot and save as html, with plotly JS library in separate file in same directory
pplot(fig, 
      filename = plotpath + '\\Cases-Tests-WI.html', 
      include_plotlyjs='cdn')


#%% Hospitalizations / Deaths

hosp_death_factor = 1

range_max = max(state_avg.Deaths.max(), state_avg.Hospitalizations.max()/hosp_death_factor)
range_deaths = np.array([-range_max * 0.05, 1.05*range_max])

fig = plotly.subplots.make_subplots()

# individual deaths bar chart
fig.add_trace(
    go.Bar(x=state.index, 
           y=state.Deaths,
           name='Deaths', 
           marker_color='rosybrown', 
           hovertemplate='%{y:.0f}'),)

# death 7-day avg
fig.add_trace(
    go.Scatter(x=state_avg.index, 
           y=state_avg.Deaths,
           name='Deaths (7-day avg)', 
           line_color='firebrick', 
           hovertemplate='%{y:.1f}'),)

# new hospitalization 7-day average
fig.add_trace(
    go.Scatter(x=state_avg.index, 
               y=state_avg.Hospitalizations, 
               name='Hospitalizations (7-day avg)', 
               line_color='darkorange', 
               hovertemplate='%{y:.1f}'),)


fig.update_yaxes({'range': range_deaths}, secondary_y=False, title_text='Daily deaths / hospitalizations')
fig.update_yaxes({'range': range_deaths*hosp_death_factor}, secondary_y=True, title_text='Daily hospitalizations')
fig.update_layout(title_text='WI Daily Deaths and Hospitalizations',
                  hovermode='x unified',
                  legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

# fig.add_annotation(dict(text='*Deaths are daily reported values, Hospitalizations are 7-day averages.',
#                         x=0.05, y=-0.1, 
#                         xref='paper', yref='paper',
#                         showarrow=False))

# plot and save as html, with plotly JS library in separate file in same directory
pplot(fig, 
      filename = plotpath + '\\Deaths-Hosp-WI.html',
      include_plotlyjs='cdn')

