#!/bin/bash

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


database="$recordingDir/dump1090/adsb_messages.db"
outdir="$recordingDir/dump1090/" # $(date +"%Y/%m")/$(date +"%Y%m%d").txt"
tempdir="/tmp"

mkdir -p $(dirname $outdir)

# draw data on the map
$baseDir/bin/heatmap.py -m 000ffffff -M 000ffffff -o $outdir/heatmap-osm.png -r 4 --margin 25 -k gaussian --height 900 --osm --sqlite_table squitters $database


# draw data on the map
$baseDir/bin/heatmap.py -o $outdir/heatmap-osm2.png -r 40 --height 900 --osm --margin 25 --sqlite_table squitters $database

# draw data on the black canvas
$baseDir/bin/heatmap.py -b black -r 30 -W 1200 -o $tempdir/h1.png -k gaussian --sqlite_table squitters $database
$baseDir/bin/heatmap.py -r 5 -W 1200 -o $tempdir/h2.png --decay 0.3 --margin 25 -k gaussian --sqlite_table squitters $database

# convert to jpg

convert -quality 83 $outdir/heatmap-osm.png $outdir/heatmap-osm.jpg
convert -quality 83 $outdir/heatmap-osm2.png $outdir/heatmap-osm2.jpg


# remove unused files
rm $tempdir/h1.png $tempdir/h2.png $outdir/heatmap-osm.png $outdir/heatmap-osm2.png