#!/bin/bash

# file to process NOAA wav file to produce weather images
# all variables are provided by noaa.sh



#
# generate map
#
$wxmapbin -T $satellite -a -H $tlefilename -o -O $duration -L "$latlonalt" $start $imgdir/$fileNameCore-mapa.png | tee -a $logFile


# process wav file with various enchancements

for enchancement in "${enchancements[@]}"    
do
    echo "**** $enchancement"
    $wxtoimgbin -e $enchancement $recdir/$fileNameCore.wav $imgdir/$fileNameCore-${enchancement}.png | tee -a $logFile
    $wxtoimgbin -e $enchancement -m $imgdir/$fileNameCore-mapa.png $recdir/$fileNameCore.wav $imgdir/$fileNameCore-${enchancement}+map.png | tee -a $logFile
done

rm $imgdir/$fileNameCore-mapa.png 
