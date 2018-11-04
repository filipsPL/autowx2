#!/bin/bash

outfile="basedir_conf.py"
pwdir=$(pwd)

echo "# this is automaticaly generated script" > $outfile
echo "# use configure.sh to generate the file" >> $outfile
echo >> $outfile
echo "baseDir=\"$pwdir/\"" >> $outfile


ln -r -f -s $outfile "bin/$outfile"

echo "Creating symlinks to the config file..."

for d in modules/*/
do
    ln -r -f -s $outfile "$d/$outfile"
done