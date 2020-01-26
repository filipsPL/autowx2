#!/bin/bash

# get the config file autowx2_conf and reports variables in a bash-like style

scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py

echo $baseDir

for line in $(python $baseDir/_listvars.py)
do
    if echo $line | grep -F = &>/dev/null
    then
        varname=$(echo "$line" | cut -d '=' -f 1)
        value=$(echo "$line" | cut -d '=' -f 2-)
        eval "$varname=$value"
    fi
done

echo $stationName

#
# add some environmental variables
#

export autowx2version=$(cd $baseDir && git describe --all)

