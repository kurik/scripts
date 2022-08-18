#!/bin/bash

SCRIPT="$0"
DIR="."
R="-maxdepth 1"

function help() {
    echo "${SCRIPT} [-r] <DIR>"
    echo "Remove all the strange characters in filenames and replace these with"
    echo "something more 'normal'"
    echo "DIR ... the directory where all the files are"
    echo "        default is '.'"
    echo "-r  ... look for files in DIR recursively "
}


# Parse args
while [[ $# -ne 0 ]]; do
    case "$1" in
        "-h"|"--help")
            help
            exit 0
            ;;
        "-r")
            R=""
            ;;
        *)
            DIR="$1"
            ;;
    esac
    shift
done

# Go through all the files
while read F; do
    stat "$F"
done < <(find "${DIR}" ${R})
