#!/bin/bash

# runs rtl_433 and scans for 433 MHz data transfers

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh

#--------------------------------------#

logfile="$recordingDir/rtl_433/"$(date +"%Y/%m")/$(date +"%Y%m%d")".txt"

mkdir -p $(dirname $logfile)

duration=$1
dongleShift=$2

mkdir -p $(dirname $logfile)

timeout --kill-after=1 $duration rtl_433 -p $dongleShift -G | tee -a $logfile
