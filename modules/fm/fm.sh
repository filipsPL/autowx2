#!/bin/bash

# test file to record fm radio for a given period of time

# directory for recorded raw and wav files
recdir='/home/dane/nasluch/sat/rec/'
# recdir="$recdirCore/"`date +"%Y/%m/%d/"`

mkdir -p $recdir

fileNameCore="$1"
satellite="$2"
start="$3"
duration="$4"
peak="$5"
azimuth="$6"
freq="$7"

# fixed values for tests
#freq="98988000"
#duration="10s"
#fileNameCore="trojka"


timeout $duration rtl_fm -f $freq -M wbfm -g 49.6 | lame -r -s 32 -m m - $recdir/$fileNameCore.mp3

