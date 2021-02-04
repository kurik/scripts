#!/bin/bash
LIGHTOFF=var/run/light.off
SONOFFMASTER="lsensor"
ONOFF=

while [[ $# -gt 0 ]]; do
    _p="$1"
    case "${_p^^}" in
        "YES"|"1"|"TRUE"|"ANO"|"PRAVDA")
            ONOFF="touch ${LIGHTOFF}"
            ;;
        "NO"|"0"|"FALSE"|"NE"|"NEPRAVDA"|"LEZ")
            ONOFF="rm -f ${LIGHTOFF}"
            ;;
    esac
    shift
done

[[ -z "${ONOFF}" ]] && { echo "Neznámý parametr. Použij ANO/NE"; exit 1; }

ssh ${SONOFFMASTER} "${ONOFF}"

exit $?
