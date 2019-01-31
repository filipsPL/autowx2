#!/usr/bin/env python
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

from autowx2_functions import *

if __name__ == "__main__":

    generatePassTableAndSaveFiles(qth)
