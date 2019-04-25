#!/bin/bash

# runs WSPR receiver

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh

#--------------------------------------#

# # # # Edit following variable with your correct data # # # #
call="SA7BNT"
gain="40"
locator="JO77PP"
hz="28.1246M"
info_rx="Start reception 10 meters"
sampling="0" #direct sampling [0,1,2] (default: 0 for Quadrature, 1 for I branch, 2 for Q branch)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##

logfile="$recordingDir/rtlsdr_wspr/"$(date +"%Y/%m")/$(date +"%Y%m%d")".txt"

mkdir -p $(dirname $logfile)

duration=$1
dongleShift=$2

mkdir -p $(dirname $logfile)

  sleep 1
      pgrep rtlsdr_wsprd > /dev/null 2>&1
       if [ $? -eq 0 ]; then
         echo $'\n'"---Kill rtlsdr_wsprd pid---" >> $logfile
        killall rtlsdr_wsprd &>> $logfile
       fi
         echo $'\n'"$(date)" >> $logfile
       echo "$info_rx"$'\n' >> $logfile
     sleep 1


cd ~/rtlsdr-wsprd
timeout --kill-after=1 $duration ./rtlsdr_wsprd -p "$dongleShift" -f "$hz" -c "$call" -l "$locator" -g "$gain" -d "$sampling" | tee -a $logfile
