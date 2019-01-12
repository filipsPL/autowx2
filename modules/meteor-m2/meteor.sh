#!/bin/bash

# module to record meteor m2 transmission
# for configuration, see meteor.conf

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh

# read module config

source $scriptDir/meteor.conf

### doing the job

mkdir -p $imgdir


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



#
# mlrpt [-f frequency -s hhmm-hhmm -t sec -qihv]
#        -f: Specify SDR Receiver Frequency (in kHz).
#        -s: Start and Stop Time in hhmm of Operation.
#        -t: Duration in min of Operation.
#        -q: Run in Quite mode (no messages printed).
#        -i: Invert (flip) Images. Useful for South to North passes.
#        -h: Print this usage information and exit.
#        -v: Print version number and exit.

### WARNING: all dates and times must be in the UTC!

startT=$(date +%H%M -d "$DATE + 1 min" -u)
stopT=$(date +%H%M -d "$DATE + $duration sec" -u)
durationMin=$(bc <<< "$duration/60 +2")

#
# recording
#
echo "$startT-$stopT, duration: $durationMin min"
mlrpt -s $startT-$stopT -t $durationMin


#
# moving recorded images to the appropriate final dir
#
mv $rawImageDir/*.jpg $imgdir/
