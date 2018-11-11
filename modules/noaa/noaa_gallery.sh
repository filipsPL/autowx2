#!/bin/bash

# NOAA sat pass gallery preparation
# generates a single html snippet with a current pass

enchancements=('MCIR-precip' 'HVC' 'MSA' 'therm' 'HVCT-precip')

# fileNameCore="$1"
# satellite="$2"
# start="$3"
# duration="$4"
# peak="$5"
# azimuth="$6"
# freq="$7"

# static values for tests
# imgdir=/home/filips/github/autowx2/recordings/noaa/img/2018/09/08/
# fileNameCore="20180908-1626_NOAA-19"
# noaaWwwDir="/home/filips/github/autowx2/recordings/noaa/"



# prorgam itself - variables
outHtml="$imgdir/$fileNameCore.html"  # html for this single pass
indexHtml="$imgdir/index.html"        # main index file for a given day
width="400px"                         # resized image width

# ---single gallery preparation------------------------------------------------#

logFile="$imgdir/$fileNameCore.log"   # log file to read from

varDate=$(sed '1q;d' $logFile)
varSat=$(sed '3q;d' $logFile)
varStart=$(sed '4q;d' $logFile)
varDur=$(sed '5q;d' $logFile)
varPeak=$(sed '6q;d' $logFile)
varFreq=$(sed '7q;d' $logFile)

# indexHtmlWww=$(date -d @$varStart +"%Y-%m-%d")  # the output of the html from template

echo "<h1>$varSat | $varDate</h1>" > $outHtml
echo "<p>f=${varFreq}Hz, peak: ${varPeak}°, duration: ${varDur}s</p>" >> $outHtml

for enchancement in "${enchancements[@]}"
do
    echo "**** $enchancement"
    obrazek="$fileNameCore-$enchancement+map.png"
    echo $obrazek

    echo "<img src='$fileNameCore-${enchancement}+map.png' alt=''$fileNameCore' width='$width'> " >> $outHtml
done

echo "<img src='$fileNameCore-spectrogram.png' alt=''spectrogram' width='$width'>" >> $outHtml


# ----consolidate data from the given day ------------------------------------#

echo "" > $indexHtml
for htmlfile in $(ls $imgdir/*.html | grep -v "index.html")
do
  cat $htmlfile >> $indexHtml
done
