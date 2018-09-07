#!/bin/bash

# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


# Track radiosondes
# more info: see https://github.com/projecthorus/radiosonde_auto_rx

duration=$1
dongleShift=$2


cd ~/progs/radiosonde_auto_rx/auto_rx/
timeout --kill-after=20 --signal=SIGINT $duration python auto_rx.py

