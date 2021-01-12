# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 17:22:35 2021

@author: 212367548
"""

import matplotlib.pyplot as plt
import numpy as np

#%% constant

t = np.arange(0,1,0.01)

q = 0.1 * np.ones(np.size(t))

plt.figure()
plt.plot(t, q)

#%%