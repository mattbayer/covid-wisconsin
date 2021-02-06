# -*- coding: utf-8 -*-
"""
Update plots for regional vaccine allocation
"""

import pandas as pd
import datetime
from plotly.offline import plot as pplot
import plotly.express as px
import covid

#%% Get the data
# Updated by UpdateData.py, just load from csv here

datapath = '.\\data'

csv_file_pop = datapath + '\\Population-Data-WI.csv'

# population data
popdata = covid.read_pop_data_wi(csv_file_pop)

# covid data
widata = covid.read_covid_data_wi('county')


#%% Sum up population by region

# get mapping between county and region
region_file = 'data\\Regions-WI.csv'

region_map = pd.read_csv(region_file)
region_map = region_map[['County',  'Modified HERC Short']]
region_map = region_map.set_index('County')
region_map = region_map.squeeze()

# get a list of region names
region_list = region_map.unique()

# add WI overall to the map
region_map['WI'] = 'WI'

# apply this map to the county name column to create a new Region column
widata['Region'] = widata.NAME.apply(lambda n: region_map[n])

# group data by regions
regiondata = widata.groupby(['Date', 'Region']).sum()
regiondata = regiondata.reset_index()

# find population of these regions
popdata_region = popdata.to_frame(name='Population')
popdata_region['Region'] = region_map

pop_region = popdata_region.groupby('Region').sum().squeeze()

#%% Trim data
col_rename = {'Date': 'Date', 
              'Region': 'Region', 
              'POS_NEW': 'Cases',
              'TEST_NEW': 'Tests',
              'DTH_NEW': 'Deaths',
              'HOSP_NEW': 'Hospitalizations',
              }

regiondata = regiondata[col_rename.keys()]
regiondata = regiondata.rename(columns=col_rename)


#%% convert per-capita (per 100K)
regiondata['RegionPop'] = regiondata.Region.apply(lambda n: pop_region[n])
capita = regiondata.copy()
datacols = ['Cases', 'Tests', 'Deaths', 'Hospitalizations']
capita[datacols] = regiondata[datacols].div(regiondata['RegionPop'], axis=0) * 100000


#%% Region names and colors
plotpath = '.\\docs\\_includes\\plotly'

regiondata['NAME'] = regiondata['Region']
region_ordered = ['Northwest', 'North Central', 'Northeast', 
                  'Western',   'Fox Valley',    'Southeast',
                  'South Central', 'Madison', 'Milwaukee']

color_dict = {'Northwest':     'thistle',
              'North Central': 'khaki',
              'Northeast':     'green',
              'Western':       'sandybrown',
              'Fox Valley':    'yellowgreen',
              'Southeast': 'lightsteelblue',
              'South Central': 'pink',
              'Madison':       'red',
              'Milwaukee':     'navy'}

colors = [color_dict[r] for r in region_ordered]



#%% Vaccine numbers
# # 25-Jan
# vaccine_region =    {'Northwest': 28443, 
#                       'North Central': 25285, 
#                       'Northeast': 30578,
#                       'Western': 17984,   
#                       'Fox Valley':23719,    
#                       'Southeast':116672,
#                       'South Central':89329, 
#                       'Madison': 49644, 
#                       'Milwaukee': 46190,
#                       'WI': 339858
#                      }

# 6-Feb
vaccine_region =     {'Northwest': 62911, 
                      'North Central': 55091, 
                      'Northeast': 64064,
                      'Western': 39936,   
                      'Fox Valley':58512,    
                      'Southeast':247299,
                      'South Central':184981, 
                      'Madison': 91797, 
                      'Milwaukee': 91308,
                      'WI': 728724
                      }

vaccine_region = pd.Series(vaccine_region)

# harmonize region naming
pop_region['Outer Southeast'] = pop_region['Southeast']
pop_region['Total Southeast'] = pop_region['Southeast'] + pop_region['Milwaukee']

vaccine_region['Outer Southeast'] = vaccine_region['Southeast'] - vaccine_region['Milwaukee']
vaccine_region['Total Southeast'] = vaccine_region['Southeast']

pop_region['Outer South Central'] = pop_region['South Central']
pop_region['Total South Central'] = pop_region['South Central'] + pop_region['Madison']

vaccine_region['Outer South Central'] = vaccine_region['South Central'] - vaccine_region['Madison']
vaccine_region['Total South Central'] = vaccine_region['South Central']

# drop these labels as now inconsistent
vaccine_region = vaccine_region.drop(['Southeast', 'South Central'])
pop_region = pop_region.drop(['Southeast', 'South Central'])

# per-capita vaccinations
vaccine_capita = vaccine_region / pop_region

# Data frame with all relevant data
vaccine_region = pd.DataFrame({'Vaccines': vaccine_region, 'Population': pop_region}, index=pop_region.index)
vaccine_region['Vaccinated %'] = vaccine_region['Vaccines'] / vaccine_region['Population'] * 100


#%% Shares of vaccine/population.
share_region = vaccine_region / vaccine_region.loc['WI']
share_region.Vaccines = pd.to_numeric(share_region.Vaccines)
share_region.Population = pd.to_numeric(share_region.Population)
share_region = share_region.drop(['WI', 'Total Southeast', 'Total South Central'], axis=0)
share_region = share_region.reset_index()

#%% Plots

plot_region = vaccine_region.loc[['Madison', 'Outer South Central', 'Milwaukee', 'Outer Southeast', 
                                'Fox Valley', 'Northeast', 'North Central', 'Northwest', 'Western']]
plot_region = plot_region.reset_index()

def perc_to_text(p):
    return '{:0.0f}'.format(p) + '%'
        
textlabels = plot_region['Vaccinated %'].apply(perc_to_text)



fig = px.bar(
    plot_region,
    x='Region',
    y='Vaccinated %',
    text=textlabels,
    color='Region',
    title='Vaccinated by region',
    color_discrete_map=color_dict,
    width=700,
    height=500,
    )

fig.update_traces(textposition='outside')


# # vaccine share vs. population share
# fig = px.bar(
#     share_region,
#     x='Region', 
#     y=['Vaccines', 'Population'], 
#     # text=textlabels,
#     # facet_col='variable', 
#     # facet_col_wrap=2,
#     # color='variable',
#     # color_discrete_sequence=col_colors,
#     # labels={'variable': '', 'Percentage':'Percent of total'},
#     barmode='group',
#     title='WI Vaccine Share by Region',
#     width=700,
#     height=700,
#     )


# # take out 'variable=' part of the axis titles
# fig.for_each_annotation(
#     lambda a: a.update(
#         text=a.text.split("=")[-1],
#         font=dict(size=15),
#         )
# #     )

# fig.update_traces(textposition='outside')
fig.update_traces(marker_line_color='gray')

# other layout
# fig.update_layout(showlegend=False)

pplot(fig,
      filename='.\\docs\\assets\\plotly\\Vaccine-Share.html',
      include_plotlyjs='cdn',
      )

# # save_png = '.\\docs\\assets\\Age-Covid_2020-12-11.png'
# save_png = '.\\docs\\assets\\Age-Covid.png'
# fig.write_image(
#     save_png,
#     width=700,
#     height=700,
#     engine='kaleido',
# )
# os.startfile(save_png)

