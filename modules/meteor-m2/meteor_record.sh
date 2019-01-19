#!/bin/bash

### WARNING: all dates and times must be in the UTC!

startT=$(date +%H%M -d "$DATE + 1 min" -u)
stopT=$(date +%H%M -d "$DATE + $duration sec" -u)
durationMin=$(bc <<< "$duration/60 +2")

#
# recording
#
echo "$startT-$stopT, duration: $durationMin min"
mlrpt -s $startT-$stopT -t $durationMin
