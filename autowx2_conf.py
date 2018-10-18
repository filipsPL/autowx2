#
# autowx2 - config file
# variables used by autowx2
#

#
# baseDir is taken from this script
# do not change, run configure.sh to configure
#
from basedir_conf import *


# satellites to record
# for list of active satellites and used frequences, see
# http://www.dk3wn.info/p/?page_id=29535

satellitesData = {
    'NOAA-18': {
        'freq': '137912500',
        'processWith': 'modules/noaa/noaa.sh',
        'priority': 2},
    'NOAA-15': {
        'freq': '137620000',
        'processWith': 'modules/noaa/noaa.sh',
        'priority': 2},
    'NOAA-19': {
        'freq': '137100000',
        'processWith': 'modules/noaa/noaa.sh',
        'priority': 2},
    'ISS': {
        #'freq': '145800000',  # FM U/v VOICE Repeater (Worldwide) and FM SSTV downlink (Worldwide) [OK]
        'freq': '143625000',  # FM VHF-1 downlink. Main Russian communications channel. Often active over Moskow. [ ]
        #'freq': '145825000', # APRS -- AX.25 1200 Bd AFSK Packet Radio (Worldwide) Downlink [ ]
        'processWith': 'modules/iss/iss_voice.sh',
        'priority': 1},
   # 'PR3_NEWS': {
   #     'freq': '98796500',
   #     'processWith': 'modules/fm/fm.sh',
   #     'fixedTime': '46 21 * * *',
   #     'fixedDuration': 30,
   #     'priority': 1},
    #'FOX-1A': {  # http://www.dk3wn.info/p/?cat=80
        #'freq': '145980000',
        #'processWith': 'modules/iss/iss_voice.sh',
        #'priority': 4},
    #'FOX-1D': {  # http://www.dk3wn.info/p/?cat=80
        #'freq': '145880000',
        #'processWith': 'modules/iss/iss_voice.sh',
        #'priority': 4},
    #'FOX-1B': {  # http://www.dk3wn.info/p/?cat=80
        #'freq': '145960000',
        #'processWith': 'modules/iss/iss_voice.sh',
        #'priority': 4},

}


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
skipFirst = 20

#
# skip last n seconds of the pass
#
skipLast = 20


# staion information
# lon: positive values for W, negative for E
stationLat = '52.34'
stationLon = '-21.06'
stationAlt = '110'
stationName = 'Warsaw'

#
# dongle gain
#
dongleGain = '49.6'


#
# recording direcotry - where to put recorded files, processed images etc. - the core
#
recordingDir = baseDir + "recordings/"


#
# location of the HTML file with a list of next passes
#
htmlNextPassList = baseDir + 'var/nextpass.html'

#
# location of the Gantt chart file with a plot of next passes; PNG or SVG file extension possible
#
ganttNextPassList = baseDir + 'var/nextpass.png'

# script tha will be used whle waiting for the next pass; set False if we just want to sleep
# by default, this script will get the parameter of duration of the time to be run and the recent dongleShift
# scriptToRunInFreeTime = False				# does nothing
scriptToRunInFreeTime = baseDir + "bin/aprs.sh" 	# APRS monitor
#scriptToRunInFreeTime = baseDir + "bin/radiosonde_auto_rx.sh" # radiosonde tracker, see https://github.com/projecthorus/radiosonde_auto_rx
#scriptToRunInFreeTime = baseDir + "bin/pymultimonaprs.sh" # APRS iGate,

# pymultimonaprs must be installed, see: https://github.com/asdil12/pymultimonaprs/
#scriptToRunInFreeTime = baseDir + "bin/dump1090.sh"


### Logging to file (enter the path) or False to disable
# logging = False
logging = recordingDir + "/logs/"


# Dongle PPM shift, hopefully this will change to reflect different PPM on freq
dongleShift = '0'

#
tleDir = baseDir + 'var/tle/'
tleFile = 'all.txt'

tleFileName = tleDir + tleFile

# dongle shift file
dongleShiftFile = baseDir + "var/dongleshift.txt"

# dongle calibration program
# should return the dongle ppm shift

calibrationTool = False # don't calibrate the dongle, use old/fixed shift
#calibrationTool = baseDir + "bin/calibrate.sh"         # uses predefined GSM channel
#calibrationTool = baseDir + "bin/calibrate_full.sh"     # check for the best GSM channel and calibrates


# DERIVATIVES #############################

#
# latlonalt for use with wxmap
#
latlonalt = "%s/%s/%s" % (stationLat, -1 * float(stationLon), stationAlt)
