#!/bin/bash

# loop over dirs, crate list of files, generates static file

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh

################## FINE TUNING #####################

# $recordingDir - real path on the system
# $wwwRootPath/recordings/logs/ - www path

# static values for tests
# imgdir=/home/filips/github/autowx2/recordings/noaa/img/2018/09/08/
# fileNameCore="20180908-1626_NOAA-19"
# wwwDir="/home/filips/github/autowx2/var/www/"


noaaDir=$recordingDir/noaa/
dirList="$wwwDir/noaa_dirlist.tmp"
htmlTemplate="$wwwDir/index.tpl"
htmlOutput="$wwwDir/index.html"
htmlOutputTable="$wwwDir/table.html"

currentDate=$(date -R)
echo $currentDate
echo "" > $dirList



# ---- NOAA list all dates and times  -------------------------------------------------#

function gallery_noaa {

howManyToday=$(ls $noaaDir/img/$(date +"%Y/%m/%d")/*.log 2> /dev/null| wc -l)

echo "<h2>NOAA recordings</h2>" >> $dirList
echo "<h4>Recent pass</h4>" >> $dirList
echo "<img src='$(cat $wwwDir/noaa-last-recording.tmp)-therm+map.th.jpg' alt='recent recording' class='img-thumbnail' />" >> $dirList
echo "<img src='$(cat $wwwDir/noaa-last-recording.tmp)-MCIR-precip+map.th.jpg' alt='recent recording' class='img-thumbnail' />" >> $dirList
echo "<img src='$(cat $wwwDir/noaa-last-recording.tmp)-HVC+map.th.jpg' alt='recent recording' class='img-thumbnail' />" >> $dirList

echo "<p></p>" >> $dirList

echo "<h4>Archive</h4>" >> $dirList
echo "<ul>" >> $dirList
echo "<li><a href='$wwwRootPath/recordings/noaa/img/$(date +"%Y/%m/%d")/index.html'>Today</a> <span class='badge badge-pill badge-light'>$howManyToday</span> </li>" >> $dirList

for y in $(ls $noaaDir/img/ | sort -n)
do
  echo "<li>$y</li><ul>" >> $dirList
  for m in $(ls $noaaDir/img/$y | sort -n)
  do
    echo "<li>($m)" >> $dirList
    for d in $(ls $noaaDir/img/$y/$m/ | sort -n)
    do
      # collect info about files in the directory
      echo "<a href='$wwwRootPath/recordings/noaa/img/$y/$m/$d/index.html'>$d</a> " >> $dirList
    done
    echo "</li>" >> $dirList
  done
  echo "</ul>" >> $dirList
done
echo "</ul>" >> $dirList

} # end function gallery noaa

# ---- METEOR list all dates and times  -------------------------------------------------#

# to be done!

# ---- ISS loop all dates and times  -------------------------------------------------#
function gallery_iss {

howManyToday=$(ls $recordingDir/iss/rec/$(date +"%Y/%m/")/*.log 2> /dev/null| wc -l)

echo "<h2>ISS recordings</h2>" >> $dirList
echo "<ul>" >> $dirList
echo "<li><a href='$wwwRootPath/recordings/iss/rec/$(date +"%Y/%m/")'>Current month</a> <span class='badge badge-pill badge-light'>$howManyToday</span>" >> $dirList

for y in $(ls $recordingDir/iss/rec/ | sort -n)
do
  echo "<li>($y) " >> $dirList
  for m in $(ls $recordingDir/iss/rec/$y | sort -n)
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
  echo "<ul>"  >> $dirList
  echo "<li><a href='$wwwRootPath/recordings/logs/$(date +"%Y-%m-%d").txt'>Today</a></li>" >> $dirList
  echo "<li><a href='$wwwRootPath/recordings/logs/'>All logs</a></li>" >> $dirList
  echo "</ul>"  >> $dirList
}

# ---- dump1090  -------------------------------------------------#

function gallery_dump1090 {
  echo "<h2>dump1090 heatmap</h2>" >> $dirList
  echo "<img src='$wwwRootPath/recordings/dump1090/heatmap-osm.jpg' alt='dump1090 heatmap' class="img-thumbnail" />" >> $dirList
  echo "<img src='$wwwRootPath/recordings/dump1090/heatmap-osm2.jpg' alt='dump1090 heatmap' class="img-thumbnail" />" >> $dirList
}


# ------------------------------------------template engine --------------------- #

# ----- RENDER APPROPRIATE PAGES ---- #

if [ "$includeGalleryNoaa" = '1' ]; then
  gallery_noaa
fi

if [ "$includeGalleryLogs" = '1' ]; then
  gallery_logs
fi

if [ "$includeGalleryISS" = '1' ]; then
  gallery_iss
fi

if [ "$includeGalleryDump1090" = '1' ]; then
  gallery_dump1090
fi


# ----- MAIN PAGE ---- #

htmlTitle="Main page"
htmlBody=$(cat $dirList)
source $htmlTemplate > $htmlOutput

# ----- PASS LIST ---- #

htmlTitle="Pass table"
htmlBody=$(cat $htmlNextPassList)
htmlBody="<p><img src='nextpass.png' alt='pass table plot' /></p>"$htmlBody

source $htmlTemplate > $htmlOutputTable
