# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 10:16:28 2021

@author: 212367548
"""

import covid

county = covid.read_covid_data_wi('county')

lacrosse = county[county.NAME=='La Crosse']

covid.plotly_casetest(lacrosse, 'POS_NEW', 'TEST_NEW', plotlabels=dict(title='La Crosse County Cases/Tests', yaxis='Cases', yaxis_secondary='New people tested'))

covid.plotly_deadhosp(lacrosse, 'DTH_NEW', 'HOSP_NEW', plotlabels=dict(title='La Crosse County Deaths/Hosp', yaxis='Deaths/Hosp'))
