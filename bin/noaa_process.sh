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
duration="$5"
peak="$6"
freq="$7"

mkdir -p `dirname ${output_file}`

date > ${output_file}.log
echo $input_file_wav >> ${output_file}.log
echo $output_file >> ${output_file}.log
echo $satellite >> ${output_file}.log
echo $start >> ${output_file}.log
echo $duration >> ${output_file}.log
echo $peak >> ${output_file}.log
echo $freq >> ${output_file}.log

$wxmapbin -T $satellite -a -H $tlefilename -o -O $duration -L "$latlonalt" $start ${output_file}-mapa.png | tee -a ${output_file}.log

for enchancement in "${enchancements[@]}"    
do
    echo "**** $enchancement"
    $wxtoimgbin -e $enchancement $input_file_wav ${output_file}-${enchancement}.png | tee -a ${output_file}.log
    $wxtoimgbin -e $enchancement -m ${output_file}-mapa.png $input_file_wav ${output_file}-${enchancement}+map.png | tee -a ${output_file}.log
done

rm ${output_file}-mapa.png
