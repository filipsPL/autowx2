##
## Config header, sorry
## TODO: Better config system
##
systemDir='/home/filips/github/autowx2/'

# satellites to record

satellitesData = {
    'NOAA-18':      {'freq': '137912500', 'decode': True, 'decodeWith': 'bin/noaa_process.sh' },
    'NOAA-15':      {'freq': '137620000', 'decode': True, 'decodeWith': 'bin/noaa_process.sh' },
    'NOAA-19':      {'freq': '137100000', 'decode': True, 'decodeWith': 'bin/noaa_process.sh' },
    'LILACSAT-1':   {'freq': '436510000', 'decode': False, 'decodeWith': False },
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



wxInstallDir='/usr/local/bin'
# Recording dir, used for RAW and WAV files
#
recdir='/home/dane/nasluch/sat/rec/'
#
# Spectrogram directory, this would be optional in the future
#
specdir='/home/dane/nasluch/sat/spectro'
#
# Output image directory
#
imgdir='/home/dane/nasluch/sat/img'
#
# Map file directory
#
mapDir='/home/dane/nasluch/sat/maps'

# Options for wxtoimg
# Create map overlay?
wxAddOverlay='yes'
# Image outputs
# Create other enhancements?
wxEnhCreate='yes'
# List of wxtoimg enhancements, please read docs
# Commons are: MCIR, MSA, MSA-precip, HVC, HVC-precip, HVCT, HVCT-precip, therm
wxEnhList = [ 'MCIR-precip', 'HVC', 'MSA', 'therm', 'HVCT-precip' ]
# Turning it off creates empty logs...
wxQuietOutput='no'
# Decode all despite low signal?
wxDecodeAll='yes'
# JPEG quality
wxJPEGQuality='72'
# Adding overlay text
wxAddTextOverlay='no'
wxOverlayText='SOME TEXT'
# Overlay offset - wxtoimg
# Negative value - push LEFT/UP
# Positive value - push RIGHT/DOWN
wxOverlayOffsetX='0'
wxOverlayOffsetY='0'
#
# Various options
# Should this script create spectrogram : yes/no
createSpectro='yes'
#
# SCP Config, works best with key authorization
#
SCP_USER=''
SCP_HOST=''
SCP_DIR=''
# Send LOG with imagefile?
LOG_SCP='n'
# Send image to remote server?
IMG_SCP='n'
# Logging
loggingEnable='y'
logFileName='/home/dane/nasluch/sat/logs/noaacapture.log'
scriptPID='/home/dane/nasluch/sat/logs/noaacapture.pid'
statusFile='/tmp/info_file'
# SFPG
sfpgLink='n'


