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

#
# Assigning variables
#

fileNameCore="$1"
satellite="$2"
start="$3"
duration="$4"
peak="$5"
azimuth="$6"
freq="$7"

#
# Saving to log file
#

logFile=$imgdir/$fileNameCore.log
echo $logFile

date > $logFile   # initialize log file
echo $fileNameCore >> $logFile
echo $satellite >> $logFile
echo $start >> $logFile
echo $duration >> $logFile
echo $peak >> $logFile
echo $freq >> $logFile


echo "fileNameCore=$fileNameCore"
echo "satellite=$satellite"
echo "start=$start"
echo "duration=$duration"
echo "peak=$peak"
echo "azimuth=$azimuth"
echo "freq=$freq"



#
# recording sumbodule
#

source $scriptDir/module_record.sh

#
# meteor gallery
#

source $scriptDir/meteor_gallery.sh
