#!/bin/bash

# file to record fm radio for a given period of time
# may be used to record ISS voice channel
# *audio saved to mp3*

# variable(s) to adjust:


# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


#### microconfiguration

recdir="$recordingDir/iss/rec/"$(date +"%Y/%m/")

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
# freq="98988000"
# duration="10s"
# fileNameCore="ISS"


### RECORDING TO MP3
echo "Recording to mp3"
timeout $duration rtl_fm -f $freq -M fm -g 49.6 -l 0 | lame -r -s 32k -m m - "$recdir/$fileNameCore.mp3"
sox "$recdir/$fileNameCore.mp3" -n spectrogram  -o "$recdir/$fileNameCore-spectrogram.png"
sox "$recdir/$fileNameCore.mp3" "$recdir/$fileNameCore-silence.mp3" silence -l 1 0.3 10% -1 2.0 10%
$baseDir/bin/multidemodulator.sh "$recdir/$fileNameCore.mp3" > "$recdir/$fileNameCore-demodulated.log"
