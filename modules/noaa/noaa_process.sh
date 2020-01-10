#!/bin/bash

# file to process NOAA wav file to produce weather images
# all variables are provided by noaa.sh



#
# generate map - only if configured to do so
#
if [ $mapOutline != 0 ]; then
  wxmap -T "$satellite" -a -H $tleFileName -o -O $duration -L "$latlonalt" $start $imgdir/$fileNameCore-mapa.png | tee -a $logFile
  withMapOutline="-m ${imgdir}/${fileNameCore}-mapa.png"
  withMapExtension="+map"
fi

#
# should we resize images?
#

if [ "$resizeimageto" != "" ]; then
  echo "Resizing images to $resizeimageto px"
  resizeSwitch="-resize ${resizeimageto}x${resizeimageto}>"
fi

#
# process wav file with various enchancements
#

for enchancement in "${enchancements[@]}"
do
    echo "**** $enhancement"
#     wxtoimg -e $enchancement $recdir/$fileNameCore.wav $imgdir/$fileNameCore-${enchancement}.png | tee -a $logFile
    wxtoimg -e $enchancement $withMapOutline $recdir/$fileNameCore.wav $imgdir/$fileNameCore-${enchancement}${withMapExtension}.png | tee -a $logFile
    convert -quality 91 $resizeSwitch $imgdir/$fileNameCore-${enchancement}${withMapExtension}.png $imgdir/$fileNameCore-${enchancement}${withMapExtension}.png
#    rm $imdir/$fileNameCore-${endhancement}+map.png
done

sox $recdir/$fileNameCore.wav -n spectrogram -o $imgdir/$fileNameCore-spectrogram.png
convert -quality 90 $imgdir/$fileNameCore-spectrogram.png $imgdir/$fileNameCore-spectrogram.jpg

rm $imgdir/$fileNameCore-mapa.png
rm $imgdir/$fileNameCore-spectrogram.png
rm $recdir/$fileNameCore.wav
