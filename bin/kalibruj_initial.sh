#!/bin/bash

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


echo
echo "*** calibrating of the dongle - looking for GSM channel..."
echo

channel=$(kal -s GSM900 -e 0 -g 49.6 | sed 's/ \+/\t/g' | cut -f 3,8 | sort -k2 -n -r | head -1 | cut -f 1)

echo "$channel" > "$baseDir/var/gsm_channel.txt"

echo "The most powerful GSM channel is $channel"

