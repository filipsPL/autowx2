###
### autowx2 - config file
### used by both - python and bash scripts ?
###



# main system dir, wher autowx is installed

systemDir='/home/filips/github/autowx2/'


# satellites to record
satellitesData = {
    'NOAA-18':      {'freq': '137912500', 'processWith': 'bin/noaa.sh' },
    'NOAA-15':      {'freq': '137620000', 'processWith': 'bin/noaa.sh' },
    'NOAA-19':      {'freq': '137100000', 'processWith': 'bin/noaa.sh' },
    'LILACSAT-1':   {'freq': '436510000', 'processWith': False },
}
    
# minimal elevation of pass to capture satellite
minElev = 20


# sttaion information
stationLat='52.34'
stationLon='-21.06'
stationAlt='110'


# script tha will be used whle waiting for the next pass; set False if we just want to sleep
# by default, this script will get the parameter of duration of the time to be run and the recent dongleShift
scriptToRunInFreeTime = False
#scriptToRunInFreeTime = "/home/filips/github/autowx2/bin/aprs.sh"


# Dongle PPM shift, hopefully this will change to reflect different PPM on freq
dongleShift='1'

#
tleDir=systemDir+'/var/tle/'
tleFile='all.txt'

tleFileName = tleDir+tleFile

# dongle shift file
dongleShiftFile=systemDir + "var/dongleshift.txt"


