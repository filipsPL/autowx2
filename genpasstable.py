#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# autowx2 - genpastable.py
# generates the pass table and recording plan for tne next few days and the appropriate plot
#
# GANTT Chart with Matplotlib
# Sukhbinder
# inspired by:
# https://sukhbinder.wordpress.com/2016/05/10/quick-gantt-chart-with-matplotlib/
# taken from
# https://github.com/fialhocoelho/test/blob/master/plot/gantt.py
#

# Import specific functions to improve code clarity
from autowx2_functions import (
    generatePassTableAndSaveFiles,
    satellitesData, stationLat, stationLon, stationAlt
)

if __name__ == "__main__":
    satellites = list(satellitesData)
    qth = (stationLat, stationLon, stationAlt)
    generatePassTableAndSaveFiles(satellites, qth)
