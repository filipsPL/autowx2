#!/bin/bash

# file to record fm radio for a given period of time
# may be used to record ISS voice channel - NOT TESTED!

# directory for recorded raw and wav files
recdir='/home/dane/nasluch/sat/rec/'

mkdir -p $recdir

fileNameCore="$1"
satellite="$2"
start="$3"
duration="$4"
peak="$5"
azimuth="$6"
freq="$7"


## M = fm or wbfm
timeout $duration rtl_fm -f $freq -M fm -g 49.6 | lame -r -s 32 -m m - $recdir/$fileNameCore.mp3