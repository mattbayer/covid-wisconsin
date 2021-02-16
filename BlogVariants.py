# -*- coding: utf-8 -*-
"""
Blog work on variants.

Created on Mon Feb 15 10:19:50 2021

@author: 212367548
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import covid
import urllib
from scipy import signal
import datetime
import os


#%% Get the data

# covid data
widata = covid.read_covid_data_wi('state')

plotdata = pd.DataFrame(index=pd.date_range(start='2021-01-10', end='2021-05-30'))
plotdata['Cases'] = widata.set_index('Date')['POS_NEW']
plotdata['Cases 7-day'] = widata.set_index('Date')['POS_NEW'].rolling(7).mean()


#%% Estimates

N = len(plotdata)

R1 = 0.81
R2 = R1*1.4
s = 5
d = np.arange(0,N)

start = 2900
frac2 = 0.02 / 4    # 2% at Jan 31; start at Jan 10 is two fraction doubling times
# frac2 = 0.001 / 4     # 0.1% at Jan 31; based on 5 positives / ~5000 sequenced

v1 = start * np.exp((R1-1)*d/s)
v2 = frac2 * start * np.exp((R2-1)*d/s)

# plt.figure()
# plt.plot(v1+v2)
# plt.plot(v2)

# plt.figure()
# plt.plot(v2/(v1+v2))

plotdata['Classic trend'] = v1
plotdata['B.1.1.7 trend'] = v2
plotdata['Model total'] = v1 + v2


#%% Plot

# fig = px.line(plotdata, y=['Cases 7-day', 'Classic', 'B.1.1.7', 'Model total'])
fig = px.area(
    plotdata, 
    y=['B.1.1.7 trend', 'Classic trend'], 
    color_discrete_sequence=['orange', 'lightsteelblue'],
    title='<i><b>Possible</i></b> B.1.1.7 variant trend in WI',
    labels={'index':'Date', 'value': 'Cases / day'}
    )

fig.add_trace(
    go.Scatter(
        x=plotdata.index,
        y=plotdata['Cases 7-day'],
        name='Cases (7-day avg)',
        marker_color='steelblue',
        )
    )

fig.update_layout(legend_traceorder='reversed', legend_title='')

            # fig.add_trace(
            #     go.Bar(
            #         x=data1.index, 
            #         y=data1.iloc[:,gg],
            #         name=data1_label, 
            #         marker_color=plotcolors[2], 
            #         hovertemplate='%{y:.0f}',
            #         showlegend=showlegend,
            #         ),
            #     row=sub_row[gg],
            #     col=sub_col[gg],
            #     )
        
# save as html, with plotly JS library loaded from CDN
htmlfile='docs\\assets\\plotly\\Variant-Estimate.html'
fig.write_html(
    file=htmlfile,
    default_height=500,
    include_plotlyjs='cdn',
    )      

pngfile = 'docs\\assets\\Variant-Estimate.png'
fig.write_image(
    pngfile,
    width=700,
    height=500,
    engine='kaleido',
    )

os.startfile(htmlfile)
os.startfile(pngfile)
