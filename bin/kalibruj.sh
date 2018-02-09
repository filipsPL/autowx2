#!/bin/bash

## calibrating of the dongle 

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py > /dev/null
source $baseDir/_listvars.sh > /dev/null


shiftFile="$baseDir/var/dongleshift.txt"
channelFile="$baseDir/var/gsm_channel.txt"
shiftHistory="$baseDir/var/shifthistory.csv"

channel=$(cat $channelFile)


#-----------------------------------------------#

mkdir -p $(dirname $shiftHistory)
recentShift=$(cat $shiftFile)

re='^-?[0-9]+([.][0-9]+)?$'
if ! [[ $recentShift =~ $re ]] ; then
   recentShift=0
fi

#kal -s GSM900 -e $recentShift

newShift=$(kal -c $channel -g 49.6 -e $recentShift 2> /dev/null | tail -1 | cut -d " " -f 4)
echo $newShift | tee $shiftFile

echo $(date +"%Y%m%d_%H:%M:%S") $(date +"%s")    $newShift >> $shiftHistory
