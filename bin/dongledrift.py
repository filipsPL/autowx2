#!/usr/bin/env python
# -*- coding: utf-8 -*-

###
### autowx2 - plot the drift of the dongle
###


import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os


scriptdir=os.path.dirname(os.path.realpath(__file__))


dongledriftfile=scriptdir+"/../var/shifthistory.csv"


drifts = np.genfromtxt(dongledriftfile, delimiter=' ', loose=True, missing_values='') 

print drifts
# create data 

exit(1)


y = [ 2,4,6,8,10,12,14,16,18,20 ]
x = [datetime.datetime.now() + datetime.timedelta(hours=i) for i in range(len(y))]
 
# plot
plt.plot(x,y)
plt.gcf().autofmt_xdate()
