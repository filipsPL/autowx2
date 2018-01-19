#!/bin/bash


logfile="/home/dane/nasluch/sat/aprs/afsk1200-`date +"%Y%m%d"`.txt"


duration=$1
dongleShift=$2

mkdir -p `dirname $logfile`


rtl_fm -f 144800000 -s 22050 -o 4 -p $dongleShift -g 49.6 | multimon-ng -a AFSK1200 -A -t raw - | tee -a $logfile