#!/bin/bash

infile="$1"

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh



sox "$infile" -b 16 --encoding signed-integer --endian little -t raw - | multimon-ng -a AFSK1200 -A -t raw -