#!/bin/bash

# fake test file to record fm radio for a given period of time

# directory for recorded raw and wav files
recdirCore='/home/dane/nasluch/sat/rec/'
recdir="$recdirCore/"`date +"%Y/%m/%d/"`

fileNameCore="$1"
satellite="$2"
start="$3"
duration="$4"
peak="$5"
freq="$6"


timeout $duration $rtlfmbin -M wbfm -f $freq | lame -r $recdir/$fileNameCore.mp3
