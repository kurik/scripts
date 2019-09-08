#!/bin/bash

function usage {
    echo "$0 [-r|-s|-h] <file/directory list>"
    echo "    -r ... play the provided list randomly (this is the default)"
    echo "    -s ... play the provided list in the sequence"
    echo "    -h ... print this help"
}

declare -i SEQ=0
declare SNDFILES="$(mktemp)"
declare FLPART="$(mktemp)"
declare FILELIST="$(mktemp)"

function cleanup {
    rm -f "${FILELIST}" "${SNDFILES}" "${FLPART}"
}

trap cleanup EXIT

# Process input params
while [[ $# -ne 0 ]]; do
    case "$1" in
        "-r")
            SEQ=0
            ;;
        "-s")
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
                find "$1" -follow ! -type d >> "${SNDFILES}"
            else
                # We have a file to play, so add it to the list
                echo "$1" >> "${SNDFILES}"
            fi
            ;;
        esac
    # Move on...
    shift
done

# $1 ... number of the line
# $2 ... the file
function get_row_n() {
    head -n $1 "$2" | tail -n 1
}

function count() {
    wc -l "$1" | cut -d ' ' -f 1
}

LNS=$(count "${SNDFILES}")
cat "${SNDFILES}" > "${FILELIST}"
N=${LNS}

[[ ${N} -eq 0 ]] && { usage ; exit 1; }

while true; do
    [[ ${SEQ} -gt 0 ]] && idx=1 || idx=$(shuf -i 1-$N -n 1)
    to_play=$(get_row_n ${idx} "${FILELIST}")
    echo "***********************************************************************************"
    echo "FROM $LNS FILES PLAYING ::" "${to_play}"
    echo "***********************************************************************************"
    MPLAYER_VERBOSE=-2 mplayer -novideo -msglevel statusline=5 -nolirc "${to_play}"

    if [[ ${N} -eq 1 ]]; then
        cat "${SNDFILES}" > "${FILELIST}"
        N=${LNS}
    else
        head -n $(( ${idx} - 1 )) "${FILELIST}" > "${FLPART}" 2>/dev/null
        tail -n $(( ${N} - ${idx} )) "${FILELIST}" >> "${FLPART}" 2>/dev/null
        cat "${FLPART}" > "${FILELIST}"
        ((N--))
    fi
done
