#!/bin/bash

# NOAA sat pass gallery preparation
# loop over passes in the given directory

scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh

# fileNameCore="$1"
# satellite="$2"
# start="$3"
# duration="$4"
# peak="$5"
# azimuth="$6"
# freq="$7"

#imgdir=/home/filips/bin/autowx2/var/www/recordings/noaa/img/2018/11/14/
#fileNameCore="20181114-1818_NOAA-18"
#noaaDir="/home/filips/bin/autowx2/var/www/recordings/noaa/"

imgdir="$1"
# curdir=$(pwd)

for logfile in $(ls $imgdir/*.log)
do
    fileNameCore=$(basename $logfile .log)
    echo $fileNameCore
    source $scriptDir/noaa_gallery.sh
done
