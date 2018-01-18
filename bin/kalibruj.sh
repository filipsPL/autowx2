#!/bin/bash

channel=115
shiftFile="/home/filips/github/autowx2/var/dongleshift.txt"
recentShift=`cat $shiftFile`

re='^-?[0-9]+([.][0-9]+)?$'
if ! [[ $recentShift =~ $re ]] ; then
   recentShift=1.5
fi

#kal -s GSM900 -e 61
kal -c $channel -g 49.6 -e $recentShift 2> /dev/null | tail -1 | cut -d " " -f 4 | tee $shiftFile
