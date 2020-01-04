#!/bin/bash

# file to record NOAA satellites via rtl_fm
# all variables are provided by noaa.sh


#
# recording here
#

echo "[DEBUG] Recording duration= ${duration}"
echo "[DEBUG] biast= ${biast}"
echo "[DEBUG] freq= ${freq}"
echo "[DEBUG] sample= ${sample}"
echo "[DEBUG] dongleGain= ${dongleGain}"
echo "[DEBUG] dongleShift= ${dongleShift}"

echo "[DEBUG] Recording"
timeout $duration rtl_fm $biast -f $freq -s $sample -g $dongleGain -F 9 -A fast -E offset -p $dongleShift $recdir/$fileNameCore.raw | tee -a $logFile

#
# transcoding here
#
echo "[DEBUG] Transcoding"
sox -t raw -r $sample -es -b 16 -c 1 -V1 $recdir/$fileNameCore.raw $recdir/$fileNameCore.wav rate $wavrate | tee -a $logFile
touch -r $recdir/$fileNameCore.raw $recdir/$fileNameCore.wav
rm $recdir/$fileNameCore.raw
