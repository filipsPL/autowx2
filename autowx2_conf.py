###
### autowx2 - config file
### variables used by autowx2
###

#
## baseDir is taken from this script
## do not change, run configure.sh to configure
#
from basedir_conf import * 



# satellites to record
satellitesData = {
    'NOAA-18':      {'freq': '137912500', 'processWith': 'modules/noaa/noaa.sh', 'priority': 1 },
    'NOAA-15':      {'freq': '137620000', 'processWith': 'modules/noaa/noaa.sh', 'priority': 1 },
    'NOAA-19':      {'freq': '137100000', 'processWith': 'modules/noaa/noaa.sh', 'priority': 1 },
    'ISS':          {'freq': '145800000', 'processWith': 'modules/iss/iss_voice.sh', 'priority': 5 },  # voice channel
    'PR3_NEWS':     {'freq': '98988000',  'processWith': 'modules/fm/fm.sh', 'fixedTime': '0,37 7-23 * * *', 'fixedDuration': 300, 'priority': 2 },
    'ISS':   {'freq': '145825000', 'processWith': 'modules/iss/iss.sh', 'priority': 5 },   # APRS - not active, not tested

}
    #'LILACSAT-1':   {'freq': '436510000', 'processWith': False },


#    
# priority time margin - time margin between two overlapping transits with different priorities, in seconds
#
priorityTimeMargin = 240


#    
# minimal elevation of pass to capture satellite
#
minElev = 20

#
# skip first n seconds of the pass
# 
skipFirst=20

#
# skip last n seconds of the pass
# 
skipLast=20


# staion information
# lon: positive values for W, negative for E
stationLat='52.34'
stationLon='-21.06'
stationAlt='110'
stationName='Warsaw'

#
# dongle gain
#
dongleGain='49.6'


#
# recording direcotry - where to put recorded files, processed images etc. - the core
#
recordingDir = baseDir + "recordings/"



#
# location of the HTML file with a list of next passes
#
htmlNextPassList=baseDir+'var/nextpass.html'

#
# location of the Gantt chart file with a plot of next passes; PNG or SVG file extension possible
#
ganttNextPassList=baseDir+'var/nextpass.png'

# script tha will be used whle waiting for the next pass; set False if we just want to sleep
# by default, this script will get the parameter of duration of the time to be run and the recent dongleShift
#scriptToRunInFreeTime = False
scriptToRunInFreeTime = baseDir + "bin/aprs.sh"


# Dongle PPM shift, hopefully this will change to reflect different PPM on freq
dongleShift='0'

#
tleDir=baseDir+'var/tle/'
tleFile='all.txt'

tleFileName = tleDir+tleFile

# dongle shift file
dongleShiftFile=baseDir + "var/dongleshift.txt"



#################################### DERIVATIVES #############################

#
# latlonalt for use with wxmap
#
latlonalt="%s/%s/%s" % (stationLat,-1*float(stationLon),stationAlt)
