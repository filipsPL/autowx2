#!/bin/bash

# file to process NOAA wav file to produce weather images
# arguments: input_file_wav output_file with no ext

latlonalt="52.250/21.000/110.0"
tlefilename="/home/filips/github/autowx2/var/tle/all.txt"
wxtoimgbin="/usr/local/bin/wxtoimg"
wxmapbin="/usr/local/bin/wxmap"

enchancements=('MCIR-precip' 'HVC' 'MSA' 'therm' 'HVCT-precip')


#-------------------------------#
# to test:
# ./noaa_process.sh tests/20180118-1504_NOAA-19.wav tests/20180118-1504_NOAA-19 NOAA-19 1516284265 926
#-------------------------------#


input_file_wav="$1"
output_file="$2"
satellite="$3"
start="$4"
duration="$4"
peak="$5"
freq="$6"

$wxmapbin -T $satellite -a -H $tlefilename -o -O $duration -L "$latlonalt" $start ${output_file}-mapa.png

for enchancement in "${enchancements[@]}"    
do
    echo $enchancement
    echo $wxtoimgbin -e $enchancement $input_file_wav ${output_file}-${enchancement}.png
    $wxtoimgbin -e $enchancement $input_file_wav ${output_file}-${enchancement}.png
    $wxtoimgbin -e $enchancement -m ${output_file}-mapa.png $input_file_wav ${output_file}-${enchancement}+map.png
done

rm $start ${output_file}-mapa.png
