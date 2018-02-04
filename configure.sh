#!/bin/bash

outfile="basedir_conf.py"

echo "# this is automaticaly generated script" > $outfile
echo "# use configure.sh to generate the file" >> $outfile
echo >> $outfile
echo "baseDir=\"`pwd`/\"" >> $outfile
