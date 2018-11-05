#!/bin/bash

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh

logfile="$recordingDir/aprs/"$(date +"%Y/%m")/$(date +"%Y%m%d")".txt"

mkdir -p $(dirname $logfile)

duration=$1
dongleShift=$2

mkdir -p $(dirname $logfile)


timeout --kill-after=1 $duration rtl_fm -f 144800000 -s 22050 -o 4 -p $dongleShift -g 49.6 | multimon-ng -a AFSK1200 -A -t raw - | tee -a $logfile
