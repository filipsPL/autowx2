#!/bin/bash

# file to process NOAA wav file to produce weather images
# all variables are provided by noaa.sh



#
# generate map
#
wxmap -T "$satellite" -a -H $tleFileName -o -O $duration -L "$latlonalt" $start $imgdir/$fileNameCore-mapa.png | tee -a $logFile


# process wav file with various enchancements

for enchancement in "${enchancements[@]}"    
do
    echo "**** $enchancement"
#     wxtoimg -e $enchancement $recdir/$fileNameCore.wav $imgdir/$fileNameCore-${enchancement}.png | tee -a $logFile
    wxtoimg -e $enchancement -m $imgdir/$fileNameCore-mapa.png $recdir/$fileNameCore.wav $imgdir/$fileNameCore-${enchancement}+map.png | tee -a $logFile
    convert -quality 93 $imgdir/$fileNameCore-${enchancement}+map.png $imgdir/$fileNameCore-${enchancement}+map.jpg
    rm $imgdir/$fileNameCore-${enchancement}+map.png
done

sox $recdir/$fileNameCore.wav -n spectrogram -o $imgdir/$fileNameCore-spectrogram.png
convert -quality 90 $imgdir/$fileNameCore-spectrogram.png $imgdir/$fileNameCore-spectrogram.jpg

rm $imgdir/$fileNameCore-mapa.png
rm $imgdir/$fileNameCore-spectrogram.png
rm $recdir/$fileNameCore.wav
