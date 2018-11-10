#!/bin/bash

# RUN radiosonde scanner for a given time
# details, see: https://github.com/projecthorus/radiosonde_auto_rx/wiki


# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


#### microconfiguration

radiosondeBin="/usr/local/bin/radiosonde_auto_rx/auto_rx/"
logfile="$recordingDir/radiosonde/log/"$(date +"%Y%m%d")".txt"
mkdir -p "$recordingDir/radiosonde/log/"

### doing the job


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

cd $radiosondeBin
timeout $duration python auto_rx.py | tee -a $logfile

