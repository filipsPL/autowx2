#!/bin/bash

# main file for recording and processing NOAA telementry data
# for configuration, see noaa.conf



# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh
source $baseDir/shell_functions.sh

#
# read configuration file
#
source $scriptDir/noaa.conf

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
debugEcho "Recording..."
source $scriptDir/noaa_record.sh

#
# execute processing script and passing all arguments to the script
#
debugEcho "Processing..."
source $scriptDir/noaa_process.sh

#
# generate gallery for a given pass
#
debugEcho "Generating gallery..."
source $scriptDir/noaa_gallery.sh

#
# generate static pages
#
debugEcho "Generating static page..."
$baseDir/bin/gen-static-page.sh
