##
## Config header, sorry
## TODO: Better config system
##
systemDir='/home/filips/github/autowx2/'

# satellites to record

satellitesData = {
    'NOAA-18':      {'freq': '137912500', 'decodeWith': 'bin/noaa_process.sh' },
    'NOAA-15':      {'freq': '137620000', 'decodeWith': 'bin/noaa_process.sh' },
    'NOAA-19':      {'freq': '137100000', 'decodeWith': 'bin/noaa_process.sh' },
    'LILACSAT-1':   {'freq': '436510000', 'decodeWith': False },
    'ISS':          {'freq': '104416000', 'decodeWith': False },
}
    
# minimal elevation
minElev = 20

stationLat='52.34'
stationLon='-21.06'
stationAlt='110'

rtl_fm_path='/usr/bin/rtl_fm'

# Dongle gain
dongleGain='49.8'
#
# Dongle PPM shift, hopefully this will change to reflect different PPM on freq
dongleShift='1'
#
# Dongle index, is there any rtl_fm allowing passing serial of dongle? Unused right now
dongleIndex='0'
#
# Sample rate, width of recorded signal - should include few kHz for doppler shift
sample ='48000'
# Sample rate of the wav file. Shouldn't be changed
wavrate='11025'
#
tleDir=systemDir+'/var/tle/'
#tleFile='weather.txt'
tleFile='all.txt'

tleFileName = tleDir+tleFile

# dongle shift file
dongleShiftFile=systemDir + "var/dongleshift.txt"

#
# Output image directory
#
imgdir='/home/dane/nasluch/sat/img'
