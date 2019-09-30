#!/bin/bash

function usage {
    echo "$0 [-r|-s|-h] <file/directory list>"
    echo "    -r ... play the provided list randomly (this is the default)"
    echo "    -s ... play the provided list in the sequence"
    echo "    -h ... print this help"
}

declare -i SEQ=0
declare TMPDIR="$(mktemp -d)"
declare PLAYLIST="${TMPDIR}/playlist"

function cleanup {
    rm -fr "${TMPDIR}"
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
                find "$1" -follow ! -type d >> "${PLAYLIST}"
            else
                # We have a file to play, so add it to the list
                echo "$1" >> "${PLAYLIST}"
            fi
            ;;
        esac
    # Move on...
    shift
done

# Do we play random ?
[[ ${SEQ} -eq 0 ]] && \
    { shuf -o "${TMPDIR}/x" "${PLAYLIST}" && mv "${TMPDIR}/x" "${PLAYLIST}"; }

function count() {
    wc -l "$1" | cut -d ' ' -f 1
}

LNS=$(count "${PLAYLIST}")

while true; do # Play forever {

while read to_play; do
    echo "*********************************************************************************"
    echo "FROM $LNS FILES PLAYING ::" "${to_play}"
    echo "*********************************************************************************"
    MPLAYER_VERBOSE=-2 mplayer -novideo -msglevel statusline=5 -nolirc "${to_play}"
done < "${PLAYLIST}";

done # Play forever }
