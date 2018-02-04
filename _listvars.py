# -*- coding: utf-8 -*-

'''
get the config file autowx2_conf and reports variables in a bash-like style
'''

from os import path

from autowx2_conf import *  # configuration

d = locals().copy()
for var in d:
    val=d[var]
    if not var.startswith("__"):		# not global variables
	if not str(val).startswith( ("{", "<") ):	# not dictionary
	    print "%s=%s" % (var, val)
