#!/bin/bash

# file to process NOAA wav file to produce weather images
# all variables are provided by noaa.sh


function removeFolderFromDirectory() {
  # This function must have two parameters:
  #   $1 - the folder name to remove
  #   $2 - the directory from which to remove $1 from
  if [ $# -lt 2 ]; then
    echo "Illegal number of parameters"
    return -1
  fi

  # Look for the directory described in $2 from the current directory
  if [ "$(ls -d */ | grep $2)" == "" ]; then
    echo "Directory [$2] not found"
    return -1
  fi

  # Find the folder described in $1 in the folder $2
  if [ $(find $2 -type d -name "$1" -prune -print) ]; then
    rm -drf $2/$1/
  fi

  return 0
}


#
# get the image file extension
#

if [ "$imageExtension" == "" ]; then
  imageExtension = "jpg"
fi

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
  wxtoimg -e $enchancement $withMapOutline $recdir/$fileNameCore.wav $imgdir/$fileNameCore-${enchancement}${withMapExtension}.png | tee -a $logFile
  convert -quality 91 $resizeSwitch $imgdir/$fileNameCore-${enchancement}${withMapExtension}.png $imgdir/$fileNameCore-${enchancement}${withMapExtension}.${imageExtension}
  if [ "$imageExtension" != "png" ]; then
      rm $imdir/$fileNameCore-${endhancement}${withMapExtension}.png
  fi
done

sox $recdir/$fileNameCore.wav -n spectrogram -o $imgdir/$fileNameCore-spectrogram.png
convert -quality 90 $imgdir/$fileNameCore-spectrogram.png $imgdir/$fileNameCore-spectrogram.jpg

rm $imgdir/$fileNameCore-mapa.png
rm $imgdir/$fileNameCore-spectrogram.png
rm $recdir/$fileNameCore.wav

# Remove old data
if [ keepDataForDays -gt 0 ]; then
  # Check the dates
  oldDate = $(date --date="$keepDataForDays days ago")

  oldYear = $(date --date="$oldDate" +%Y)
  oldMonth = $(date --date="$oldDate" +%m)
  oldDay = $(date --date="$oldDate" +%d)

  newYear = $(date +%Y)
  newMonth = $(date +%m)
  newDay = $(date +%d)

  # Remove data
  if [ $oldYear -ne $newYear ]; then
    # The old year is different than the new year (ie old year is the previous year). Therefore,
    # just remove the entire directory.
    removeFolderFromDirectory $oldYear $rootImgDir
    removeFolderFromDirectory $oldYear $rootRecDir
  elif [ $oldMonth -ne $newMonth ]; then
    # The old month is different than the new month (ie old month is the previous month). Therefore,
    # just remove the entire directory.
    removeFolderFromDirectory $oldMonth $rootImgDir/$oldYear
    removeFolderFromDirectory $oldMonth $rootRecDir/$oldYear
  elif [ $oldDay -ne $newDay ]; then
    # The old day is different than the new day (ie old day is the previous day). Therefore,
    # just remove the entire directory.
    removeFolderFromDirectory $oldYear $rootImgDir/$oldYear/$oldMonth
    removeFolderFromDirectory $oldYear $rootRecDir/$oldYear/$oldMonth
  fi

fi
