#!/bin/bash

N=$#


function get_idx {
    R=${RANDOM}
    R=$(( ${R} + $(date +%s) ))
    echo "${R:5} % $1 + 1" | bc
}

while true; do
    to_play_idx=$(get_idx $N)
    echo "***********************************************************************************"
    echo 'PLAYING: ' $to_play_idx "/" $N "::" "${!to_play_idx}"
    echo "***********************************************************************************"
    mplayer -novideo "${!to_play_idx}"
done
