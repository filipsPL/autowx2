#!/bin/bash

# main file for recording and processing NOAA telementry data


# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh

################## FINE TUNING #####################

# directory with noaa stuff
noaaDir="$recordingDir/noaa/"

# directory for generated images
imgdir="$noaaDir/img/"$(date +"%Y/%m/%d/")

# directory for recorded raw and wav files
recdir="$noaaDir/rec/"$(date +"%Y/%m/%d/")


#
# Sample rate, width of recorded signal - should include few kHz for doppler shift
sample='48000'
# Sample rate of the wav file. Shouldn't be changed
wavrate='11025'

#
# Dongle index, is there any rtl_fm allowing passing serial of dongle?
dongleIndex='0'

# enchancements to apply to the pocessed images. See wxtoimg manual for available options
enchancements=('MCIR-precip' 'HVC' 'MSA' 'therm' 'HVCT-precip', 'NO')



##################################################


#fileNameCore, satellite, start, duration+towait, peak, freq

fileNameCore="$1"
satellite="$2"
start="$3"
duration="$4"
peak="$5"
azimuth="$6"
freq="$7"

echo "fileNameCore=$fileNameCore"
echo "satellite=$satellite"
echo "start=$start"
echo "duration=$duration"
echo "peak=$peak"
echo "azimuth=$azimuth"
echo "freq=$freq"

echo "sample=$sample"
echo "wavrate=$wavrate"
echo "dongleIndex=$dongleIndex"
echo "enchancements=${enchancements}"


#-------------------------------#
# to test the processing part:
# comment the recording part and uncomment the following part
# ./noaa.sh tests/20180118-1504_NOAA-19.wav tests/20180118-1504_NOAA-19 NOAA-19 1516284265 926
# fileNameCore="20180118-1504_NOAA-19"
# satellite="NOAA-19"
# start="1516284265"
# duration="926"
# peak="82"
# freq="144"
# imgdir="tests/"
# recdir="tests/"
#-------------------------------#



#
# create directories
#

mkdir -p $imgdir
mkdir -p $recdir

#
# logs are very important!
#
logFile=$imgdir/$fileNameCore.log

date > $logFile   # initialize log file
echo $fileNameCore >> $logFile
echo $satellite >> $logFile
echo $start >> $logFile
echo $duration >> $logFile
echo $peak >> $logFile
echo $freq >> $logFile


#
# execute recordigng scriptDir and passing all arguments to the script
#

source $scriptDir/noaa_record.sh

#
# execute processing script and passing all arguments to the script
#

source $scriptDir/noaa_process.sh

#
# generate gallery for a given pass
#

source $scriptDir/noaa_gallery.sh

#
# generate static pages
#

$baseDir/bin/gen-static-page.sh
