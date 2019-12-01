#!/bin/bash

WD="${1:-$(pwd)}"

find "${WD}" -type f | \
while read F; do 
    MI=$(mediainfo '--Output=Video;%Format%:%CodecID%' "$F")
    echo "$(ls -l "$F" | awk '{print $5}') $F#$MI"
done
