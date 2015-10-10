#!/bin/bash

DAYSTOKEEP=40
TESTMODE=""

function usage {
    echo "Usage:"
    echo "$(basename $0) [-h|--help] [-t|--test] [-d|--days <days>]"
    echo "    -h|--help ... print this help"
    echo "    -t|--test ... test/dry mode"
    echo "    -d|--days ... number of days to keep photos"
    echo
}

while [[ $# -ne 0 ]]; do
    case "$1" in
        "-d"|"--days")
            shift
            DAYSTOKEEP="$1"
            ;;
        "-h"|"--help")
            usage
            exit 0
            ;;
        "-t"|"--test")
            TESTMODE="True"
            ;;
        *)
            echo "Invalid parameter >>$1<<"
            usage
            exit 1
            ;;
    esac
    shift
done

DIR="$(date +'%Y%m%d')"
for d in *; do
    [[ ${d} -ge 19700101 ]] 2>/dev/null || continue
    timediff=$(( $(date +%s -d ${DIR}) - $(date +%s -d ${d}) )) 2>/dev/null
    if [[ ${timediff} -gt $(( ${DAYSTOKEEP} * 3600 * 24 )) ]]; then
        if [[ -z "${TESTMODE}" ]]; then
            rm -rf ${d}
        else
            echo "Smazat: " ${d} "timedif:" ${timediff}
        fi
    else
        if [[ -n "${TESTMODE}" ]]; then
            echo "Ponechat: " ${d} "timedif:" ${timediff}
        fi
    fi
done

exit 0
