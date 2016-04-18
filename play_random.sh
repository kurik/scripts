#!/bin/bash

function usage {
    echo "$0 [-r|-s|-h] <file/directory list>"
    echo "    -r ... play the provided list randomly (this is the default)"
    echo "    -s ... play the provided list in the sequence"
    echo "    -h ... print this help"
}

RND=1
SEQ=0

# Process input params
declare -a SNDFILES
while [[ $# -ne 0 ]]; do
    case "$1" in
        "-r")
            RND=1
            SEQ=0
            ;;
        "-s")
            RND=0
            SEQ=1
            ;;
        "-h")
            usage
            exit 0
            ;;
        "-*")
            echo "Invalid switch $1" 1>2
            usage
            exit 1
            ;;
        *)
            if [[ -d "$1" ]]; then
                # We have a directory; add all files in the directory to the list of files to play
                while read F; do
                    SNDFILES=("${SNDFILES[@]}" "${F}")
                done < <(find "$1" -follow ! -type d | sort)
            else
                # We have a file to play, so add it to the list
                SNDFILES=("${SNDFILES[@]}" "$1")
            fi
            ;;
        esac
    # Move on...
    shift
done


function get_idx {
    if [[ ${RND} -ne 0 ]]; then
        R=${RANDOM}
        R=$(( ${R} + $(date +%s) ))
        echo "${R:5} % $1" | bc
    else
        [[ $1 -eq $(( $2 + 1 )) ]] && echo 0 || echo $(( $2 + 1 ))
    fi
}

N=${#SNDFILES[@]}
oldidx=-1

while true; do
    to_play_idx=$(get_idx ${N} ${oldidx})
    echo "***********************************************************************************"
    echo 'PLAYING: ' $(( $to_play_idx + 1 )) "/" $N "::" "${SNDFILES[${to_play_idx}]}"
    echo "***********************************************************************************"
    mplayer -novideo "${SNDFILES[${to_play_idx}]}"
    oldidx=${to_play_idx}
done
