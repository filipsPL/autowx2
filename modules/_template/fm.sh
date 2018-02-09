#!/bin/bash

# test file to record fm radio for a given period of time


# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


#### microconfiguration

recdir="$recordingDir/fm/rec/"$(date +"%Y/%m/")

### doing the job

mkdir -p $recdir

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


# fixed values for tests
#freq="98988000"
#duration="10s"
#fileNameCore="trojka"


timeout $duration rtl_fm -f $freq -M wbfm -g 49.6 | lame -r -s 32 -m m - $recdir/$fileNameCore.mp3

