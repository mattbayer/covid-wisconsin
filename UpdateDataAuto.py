# -*- coding: utf-8 -*-
"""
Update data from WI DHS automatically using Github Actions.

Created on Thu Dec 24 12:33:03 2020

@author: Matt Bayer
"""

import covid

covid.update_covid_data_wi('state')
covid.update_covid_data_wi('county')