#!/bin/bash

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py

###

TLEDIR=$baseDir/var/tle/

rm $TLEDIR/weather.txt
wget --no-check-certificate -r http://www.celestrak.com/NORAD/elements/weather.txt -O $TLEDIR/weather.txt

#rm $TLEDIR/noaa.txt
#wget -r http://www.celestrak.com/NORAD/elements/noaa.txt -O $TLEDIR/noaa.txt

rm $TLEDIR/amateur.txt
wget -r http://www.celestrak.com/NORAD/elements/amateur.txt -O $TLEDIR/amateur.txt

rm $TLEDIR/cubesat.txt
wget -r http://www.celestrak.com/NORAD/elements/cubesat.txt -O $TLEDIR/cubesat.txt


rm $TLEDIR/multi.txt
wget -r http://www.pe0sat.vgnet.nl/kepler/mykepler.txt -O $TLEDIR/multi.txt

rm $TLEDIR/all.txt
cat $TLEDIR/*.txt > $TLEDIR/all.txt

date
echo Updated