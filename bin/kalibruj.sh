#!/bin/bash

## calibrating of the dongle 

channel=23

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

shiftFile="$DIR/../var/dongleshift.txt"
shiftHistory="$DIR/../shifthistory.csv"

#-----------------------------------------------#

mkdir -p `dirname $shiftHistory`
recentShift=`cat $shiftFile`

re='^-?[0-9]+([.][0-9]+)?$'
if ! [[ $recentShift =~ $re ]] ; then
   recentShift=1.5
fi

#kal -s GSM900 -e 61

newShift=`kal -c $channel -g 49.6 -e $recentShift 2> /dev/null | tail -1 | cut -d " " -f 4`
echo $newShift | tee $shiftFile

echo `date +"%Y%m%d_%H:%M:%S"` `date +"%s"`    $newShift >> $shiftHistory
