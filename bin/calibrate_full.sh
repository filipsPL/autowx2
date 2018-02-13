#!/bin/bash

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines

scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py > /dev/null
source $baseDir/_listvars.sh > /dev/null


channel=$(timeout --kill-after=1 300 kal -s GSM900 -e 0 -g 49.6 2> /dev/null | sed 's/ \+/\t/g' | cut -f 3,8 | sort -k2 -n -r | head -1 | cut -f 1)
echo "$channel" > "$baseDir/var/gsm_channel.txt"


source $baseDir/bin/calibrate.sh

