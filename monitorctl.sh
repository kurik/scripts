#!/bin/bash

INT="eDP-1"
EXT="DP-2-3"
EXT_PROBE="${EXT} connected"
EXT_PROBE2="${EXT} connected [0-9]"
EXT_PROBE3="${EXT} connected primary [0-9]"

XR="/usr/bin/xrandr"
export DISPLAY=":0"
export XAUTHORITY=/home/jkurik/.Xauthority
PSCFG="/home/jkurik/.config/plasma-org.kde.plasma.desktop-appletsrc"
PSCFG2="/home/jkurik/.config/plasmashellrc"

STAT_ON="on"
STAT_OFF="off"
STAT_DISC="disconnected"

function ext_status {
    XRSTAT="$(${XR} -q 2>&1)"
    echo "${XRSTAT}" | grep -e "${EXT_PROBE3}" -e "${EXT_PROBE2}" &>/dev/null && { echo "${STAT_ON}"; return; }
    echo "${XRSTAT}" | grep "${EXT_PROBE}" &>/dev/null && { echo "${STAT_OFF}"; return; }
    echo "${STAT_DISC}"

    return 0
}

function ext_profile {
    cp "${PSCFG}" "${PSCFG}".jku
    cp "${PSCFG2}" "${PSCFG2}".jku
    /usr/bin/kquitapp5 plasmashell; wait
    case "${1}" in
        "on")
            "${XR}" --output "${EXT}" --off #--output "${INT}" --off
            "${XR}" --output "${EXT}" --auto --left-of "${INT}" --output "${INT}" --auto
            "${XR}" --output "${EXT}" --primary
            ;;
        "off")
            "${XR}" --output "${EXT}" --off #--output "${INT}" --off
            "${XR}" --output "${EXT}" --off --output "${INT}" --auto --primary
            ;;
        *)
            echo "Invalid external profile" 2>&1
            /usr/bin/plasmashell &
            exit 1
    esac
    cp "${PSCFG}".jku "${PSCFG}"
    cp "${PSCFG2}".jku "${PSCFG2}"
    /usr/bin/plasmashell &>/dev/null &
}



case "${1}" in
    "on")
        [[ $(ext_status) != "${STAT_ON}" ]] && ext_profile "${STAT_ON}"
        ;;
    "off")
        ext_profile "${STAT_OFF}"
        ;;
    ""|"auto") # Auto mode
        case "$(ext_status)" in
            "${STAT_OFF}")
                ext_profile "${STAT_ON}"
                ;;
            "${STAT_DISC}")
                [[ $(ext_status) != "${STAT_DISC}" ]] && ext_profile "${STAT_OFF}"
                ;;
        esac
        ;;
    "status")
        ext_status
        ;;
    *)
        echo "Invalid external profile" 2>&1
        exit 1
esac


exit 0
#
