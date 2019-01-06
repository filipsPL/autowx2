#!/bin/bash

# test file to record fm radio for a given period of time


# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


################## FINE TUNING #####################

# directory with noaa stuff
meteorDir="$recordingDir/meteor/"

# directory for generated images
imgdir="$meteorDir/img/"$(date +"%Y/%m/%d/")

# directory for recorded raw and wav files
recdir="$meteorDir/rec/"$(date +"%Y/%m/%d/")

### doing the job

mkdir -p $recdir $imgdir


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
freq=137.9M
duration="120"
fileNameCore="meteor"

#
# mlrpt [-f frequency -s hhmm-hhmm -t sec -qihv]
#        -f: Specify SDR Receiver Frequency (in kHz).
#        -s: Start and Stop Time in hhmm of Operation.
#        -t: Duration in min of Operation.
#        -q: Run in Quite mode (no messages printed).
#        -i: Invert (flip) Images. Useful for South to North passes.
#        -h: Print this usage information and exit.
#        -v: Print version number and exit.

startT=$(date +%H%M -d "$DATE + 1 min" -u)
stopT=$(date +%H%M -d "$DATE + $duration sec" -u)

echo $startT-$stopT

mlrpt -f $freq -s $startT-$stopT
# mlrpt -f $freq -s 0801-0803
