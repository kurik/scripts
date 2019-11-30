#!/bin/bash

function usage {
    echo "$0 [-r|-s|-h] <file/directory list>"
    echo "    -r ... play the provided list randomly (this is the default)"
    echo "    -s ... play the provided list in the sequence"
    echo "    -h ... print this help"
}

declare SHUFFLE=1
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
            SHUFFLE=1
            ;;
        "-s")
            SHUFFLE=0
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
                find "$1" -follow ! -type d -exec readlink -f {} \; >> "${PLAYLIST}"
            else
                # We have a file to play, so add it to the list
                readlink -f "$1" >> "${PLAYLIST}"
            fi
            ;;
        esac
    # Move on...
    shift
done

function shuffle() {
    SHUFF="${PLAYLIST}.$$"
    shuf -o "${SHUFF}" < "${PLAYLIST}" || \
        { echo 'Error shuffling files'; return 1; }
    mv "${SHUFF}" "${PLAYLIST}" || \
        { echo "Can not rename ${SHUFF} to ${PLAYLIST}"; return 1; }
    return 0
}

while true; do
    # Random order ?
    [[ $SHUFFLE -ne 0 ]] && { shuffle || exit 1; }

    # Play the whole playlist
    MPLAYER_VERBOSE=-2 mplayer \
        -novideo \
        -nolirc \
        -msglevel all=0:input=5:statusline=5 \
        -playlist "${PLAYLIST}" \
        || { echo "Error playing playlist"; exit 1; }
done

exit 0
#EOF
