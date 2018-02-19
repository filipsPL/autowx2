#!/bin/bash

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


database="$baseDir/recordings/dump1090/adsb_messages.db"

mkdir -p $(dirname $database)

duration=$1
dongleShift=$2


timeout --kill-after=1 $duration dump1090 --quiet --metric --net --aggressive --ppm $dongleShift &
timeout --kill-after=1 $duration /home/filips/github/dump1090-heatmaps/dump1090-stream-parser.py --database $database