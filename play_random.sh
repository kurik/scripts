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
        echo 0
    fi
}

FILELIST=("${SNDFILES[@]}")
N=${#SNDFILES[@]}

while true; do
    to_play_idx=$(get_idx ${#FILELIST[@]})
    echo "***********************************************************************************"
    echo "FROM $N FILES PLAYING ::" "${FILELIST[${to_play_idx}]}"
    echo "***********************************************************************************"
    mplayer -novideo "${FILELIST[${to_play_idx}]}"

    if [[ ${#FILELIST[@]} -eq 1 ]]; then
        FILELIST=("${SNDFILES[@]}")
        echo "EXIT"
    else
        xlist=()
        idx=0
        for i in "${FILELIST[@]}"; do
            if [[ ${idx} -ne ${to_play_idx} ]]; then
                xlist=("${xlist[@]}" "$i")
            fi
            idx=$(( ${idx} + 1 ))
        done
        FILELIST=("${xlist[@]}")
    fi
done
