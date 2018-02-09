#!/bin/bash

# main file for recording and processing NOAA telementry data
# configuration file: noaa.conf in the current directory



scriptDir="$(dirname "$(realpath "$0")")"

# read config from the NOAA config file
source $scriptDir/noaa.conf

#fileNameCore, satellite, start, duration+towait, peak, freq

fileNameCore="$1"
satellite="$2"
start="$3"
duration="$4"
peak="$5"
azimuth="$6"
freq="$7"

#-------------------------------#
# to test the processing part:
# comment the recording part and uncomment the following part
# ./noaa.sh tests/20180118-1504_NOAA-19.wav tests/20180118-1504_NOAA-19 NOAA-19 1516284265 926
fileNameCore="20180118-1504_NOAA-19"
satellite="NOAA-19"
start="1516284265"
duration="926"
peak="82"
freq="144"
imgdir="tests/"
recdir="tests/"
#-------------------------------#


echo "fileNameCore=$fileNameCore"
echo "satellite=$satellite"
echo "start=$start"
echo "duration=$duration"
echo "peak=$peak"
echo "azimuth=$azimuth"
echo "freq=$freq"


#
# execute processing script and passing all arguments to the script
#

source $scriptDir/noaa_process.sh
