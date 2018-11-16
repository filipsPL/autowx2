#!/bin/bash

# loop over dirs, crate list of files, generates static file

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh

################## FINE TUNING #####################


# static values for tests
# imgdir=/home/filips/github/autowx2/recordings/noaa/img/2018/09/08/
# fileNameCore="20180908-1626_NOAA-19"
# wwwDir="/home/filips/github/autowx2/var/www/"


noaaDir=$recordingDir/noaa/
dirList="$wwwDir/noaa_dirlist.html"
htmlTemplate="$wwwDir/index.tpl"
htmlOutput="$wwwDir/index.html"
htmlOutputTable="$wwwDir/table.html"


# ----list all dates and times  -------------------------------------------------#

echo "<ul>" > $dirList
for y in $(ls $noaaDir/img/ | sort -rn)
do
  echo "<li>$y</li><ul>" >> $dirList
  for m in $(ls $noaaDir/img/$y | sort -rn)
  do
    echo "<li>($m)" >> $dirList
    for d in $(ls $noaaDir/img/$y/$m/ | sort -rn)
    do
      # collect info about files in the directory
      echo "<a href='recordings/noaa/img/$y/$m/$d/index.html'>$d</a> " >> $dirList
    done
    echo "</li>" >> $dirList
  done
  echo "</ul>" >> $dirList
done
echo "</ul>" >> $dirList


# ------------------------------------------template engine --------------------- #

htmlTitle="Main page"
htmlBody=$(cat $dirList)
source $htmlTemplate > $htmlOutput

# ----- PASS LIST ---- #


htmlTitle="Pass list"
htmlBody=$(cat $htmlNextPassList)
htmlBody="<p><img src='nextpass.png' alt='pass table plot' /></p>"$htmlBody

source $htmlTemplate > $htmlOutputTable
