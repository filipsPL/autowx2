#!/bin/bash

# tasks to perform daily

scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py > /dev/null
source $baseDir/_listvars.sh > /dev/null

# generate home page from template
$baseDir/genpasstable.py 1>/dev/null 2>&1
$baseDir/bin/gen-static-page.sh 1>/dev/null 2>&1




# update Keplers
$baseDir/bin/update-keps.sh 1>$recordingDir/logs/keps-update.txt 2>&1

