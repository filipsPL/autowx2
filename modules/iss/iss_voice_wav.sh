#!/bin/bash

# file to record fm radio for a given period of time
# may be used to record ISS voice channel, or wav to SSTV conversion
# audio files saved to wav!


# variable(s) to adjust:


# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


#### microconfiguration

recdir="$recordingDir/iss/rec/"$(date +"%Y/%m/")
sample="44000"

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


### fixed values for tests
# freq="98988000"
# duration="10s"
# fileNameCore="ISS"

### RECORDING TO WAV, for further processing, eg, for SSTV
echo "Recording to wav"
timeout $duration rtl_fm -f $freq -s $sample -g $dongleGain -F 9 -A fast -E offset -p $dongleShift $recdir/$fileNameCore.raw | tee -a $logFile
sox -t raw -r $sample -es -b 16 -c 1 -V1 $recdir/$fileNameCore.raw $recdir/$fileNameCore.wav rate $wavrate | tee -a $logFile
touch -r $recdir/$fileNameCore.raw $recdir/$fileNameCore.wav
rm $recdir/$fileNameCore.raw
