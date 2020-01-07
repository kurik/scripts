#!/bin/bash

ffmpeg -i "${1}" -vn -ar 44100 -ac 2 -b:a 320k "${1%.*}.mp3"
exit $?

#EOF
