# -*- coding: utf-8 -*-
"""
Update data from WI DHS automatically using Github Actions.

Created on Thu Dec 24 12:33:03 2020

@author: Matt Bayer
"""


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


