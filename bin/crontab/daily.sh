#!/bin/bash

# tasks to perform daily

scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py > /dev/null
source $baseDir/_listvars.sh > /dev/null

# generate home page from template
$baseDir/genpasstable.py 1>/dev/null 2>&1
$baseDir/bin/gen-static-page.sh 1>/dev/null 2>&1


# generate heatmap for dump1090
$baseDir/bin/dump1090-draw_heatmap.sh 1>/dev/null 2>&1

