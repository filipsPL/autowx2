#!/bin/bash

# file to record fm radio for a given period of time
# may be used to record ISS voice channel

# variable(s) to adjust:

#recordTo="wav" # record to wav file
recordTo="mp3"  # record to mp3 file


# read the global configuration file autowx2_conf.py via the bash/python configuration parser
# do not change the following three lines
scriptDir="$(dirname "$(realpath "$0")")"
source $scriptDir/basedir_conf.py
source $baseDir/_listvars.sh


#### microconfiguration

recdir="$recordingDir/iss/rec/"$(date +"%Y/%m/")

### doing the job

mkdir -p $recdir

fileNameCore="$1"
satellite="$2"
start="$3"
duration="$4"
peak="$5"
azimuth="$6"
freq="$7"


echo "fileNameCore=$fileNameCore"
echo "satellite=$satellite"
echo "start=$start"
echo "duration=$duration"
echo "peak=$peak"
echo "azimuth=$azimuth"
echo "freq=$freq"



# fixed values for tests
# freq="98988000"
# duration="10s"
# fileNameCore="ISS"


## M = fm or wbfm
# command1="timeout $duration rtl_fm -f $freq -M fm -g 49.6"
# command2="lame -r -s 32 -m m - $recdir/$fileNameCore.mp3"
# command3="sox -t raw -r $sample -es -b 16 -c 1 -V1 -n spectrogram - -o $recdir/$fileNameCore-spectrogram.png"
# { "$command1" 2>&3 | "$command2"; } 3>&1 1>&2 | "$command3"


###timeout $duration rtl_fm -f $freq -M fm -g 49.6 | sox -traw -r24k -es -b16 -c1 -V1 - -tmp3 "$recdir/$fileNameCore.mp3"


if [ ${recordTo} == 'mp3' ]; then
  ### RECORDING TO MP3
  echo "Recording to mp3"
  timeout $duration rtl_fm -f $freq -M fm -g 49.6 -l 0 | lame -r -s 32k -m m - "$recdir/$fileNameCore.mp3"
  sox "$recdir/$fileNameCore.mp3" -n spectrogram  -o "$recdir/$fileNameCore-spectrogram.png"
  sox "$recdir/$fileNameCore.mp3" "$recdir/$fileNameCore-silence.mp3" silence -l 1 0.3 10% -1 2.0 10%
  $baseDir/bin/multidemodulator.sh "$recdir/$fileNameCore.mp3" > "$recdir/$fileNameCore-demodulated.log"

elif [ ${recordTo} == 'wav' ]; then
  ### RECORDING TO WAV, for further processing, eg, for SSTV
  echo "Recording to wav"
  timeout $duration rtl_fm -f $freq -s $sample -g $dongleGain -F 9 -A fast -E offset -p $dongleShift $recdir/$fileNameCore.raw | tee -a $logFile
  sox -t raw -r $sample -es -b 16 -c 1 -V1 $recdir/$fileNameCore.raw $recdir/$fileNameCore.wav rate $wavrate | tee -a $logFile
  touch -r $recdir/$fileNameCore.raw $recdir/$fileNameCore.wav
  rm $recdir/$fileNameCore.raw
fi
