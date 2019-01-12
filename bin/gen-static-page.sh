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
dirList="$wwwDir/noaa_dirlist.tmp"
htmlTemplate="$wwwDir/index.tpl"
htmlOutput="$wwwDir/index.html"
htmlOutputTable="$wwwDir/table.html"

currentDate=$(date)
echo $currentDate


echo "" > $dirList

# ---- NOAA list all dates and times  -------------------------------------------------#

function gallery_noaa {

echo "<h2>NOAA recordings</h2>" >> $dirList
echo "<h4>Recent pass</h4>" >> $dirList
echo "<img src='$(cat $wwwDir/noaa-last-recording.tmp)-therm+map.th.jpg' alt='recent recording' class='img-thumbnail' />" >> $dirList
echo "<img src='$(cat $wwwDir/noaa-last-recording.tmp)-MCIR-precip+map.th.jpg' alt='recent recording' class='img-thumbnail' />" >> $dirList
echo "<img src='$(cat $wwwDir/noaa-last-recording.tmp)-HVC+map.th.jpg' alt='recent recording' class='img-thumbnail' />" >> $dirList
# echo "<a href='$(cat $wwwDir/noaa-last-recording.tmp).html'>see more</a>" >> $dirList

echo "<h4>Archive</h4>" >> $dirList
echo "<ul>" >> $dirList
for y in $(ls $noaaDir/img/ | sort -rn)
do
  echo "<li>$y</li><ul>" >> $dirList
  for m in $(ls $noaaDir/img/$y | sort -rn)
  do
    echo "<li>($m)" >> $dirList
    for d in $(ls $noaaDir/img/$y/$m/ | sort -rn)
    do
      # collect info about files in the directory
      echo "<a href='$wwwRootPath/recordings/noaa/img/$y/$m/$d/index.html'>$d</a> " >> $dirList
    done
    echo "</li>" >> $dirList
  done
  echo "</ul>" >> $dirList
done
echo "</ul>" >> $dirList

}

# ---- ISS loop all dates and times  -------------------------------------------------#
function gallery_iss {

echo "<h2>ISS recordings</h2>" >> $dirList
echo "<ul>" >> $dirList
for y in $(ls $noaaDir/img/ | sort -rn)
do
  echo "<li>($y) " >> $dirList
  for m in $(ls $noaaDir/img/$y | sort -rn)
  do
    echo "<a href='$wwwRootPath/recordings/iss/rec/$y/$m/'>$m</a> " >> $dirList
  done
  echo "</li>" >> $dirList
done
echo "</ul>" >> $dirList

}

# ---- LOGS  -------------------------------------------------#

function gallery_logs {
  echo "<h2>Logs</h2>" >> $dirList
  echo "<ul><li>(All) <a href='$wwwRootPath/recordings/logs/'>Logs</a></li></ul>" >> $dirList
}

# ---- dump1090  -------------------------------------------------#

function gallery_dump1090 {
  echo "<h2>dump1090 heatmap</h2>" >> $dirList
  echo "<img src='$wwwRootPath/recordings/dump1090/heatmap-osm.jpg' alt='dump1090 heatmap' class="img-thumbnail" />" >> $dirList
  echo "<img src='$wwwRootPath/recordings/dump1090/heatmap-osm2.jpg' alt='dump1090 heatmap' class="img-thumbnail" />" >> $dirList
}


# ------------------------------------------template engine --------------------- #

# ----- RENDER APPROPRIATE PAGES ---- #

gallery_noaa
gallery_logs
gallery_iss

# ----- MAIN PAGE ---- #

autowx2version=$(git describe --tags)
htmlTitle="Main page"
htmlBody=$(cat $dirList)
source $htmlTemplate > $htmlOutput

# ----- PASS LIST ---- #


htmlTitle="Pass table"
htmlBody=$(cat $htmlNextPassList)
htmlBody="<p><img src='nextpass.png' alt='pass table plot' /></p>"$htmlBody

source $htmlTemplate > $htmlOutputTable
