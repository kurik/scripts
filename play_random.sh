#!/bin/bash

# Process input params
declare -a SNDFILES
while [[ $# -ne 0 ]]; do
    if [[ -d "$1" ]]; then
        # We have a directory; add all files in the directory to the list of files to play
        while read F; do
            SNDFILES=("${SNDFILES[@]}" "${F}")
        done < <(find "$1" ! -type d)
    else
        # We have a file to play, so add it to the list
        SNDFILES=("${SNDFILES[@]}" "$1")
    fi
    # Move on...
    shift
done


function get_idx {
    R=${RANDOM}
    R=$(( ${R} + $(date +%s) ))
    echo "${R:5} % $1" | bc
}

N=${#SNDFILES[@]}

while true; do
    to_play_idx=$(get_idx ${N})
    echo "***********************************************************************************"
    echo 'PLAYING: ' $(( $to_play_idx + 1 )) "/" $N "::" "${SNDFILES[${to_play_idx}]}"
    echo "***********************************************************************************"
    mplayer -novideo "${SNDFILES[${to_play_idx}]}"
done
