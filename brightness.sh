#!/bin/bash

MONITOR="eDP-1"
STEP=0.1
CURRENT=$(xrandr --current --verbose | sed -n '/^'${MONITOR}' connected/,/^\s*Brightness:/{s/^\s*Brightness:\s*// p}')
NEW=${CURRENT}

case $1 in
    [uU]*)
        NEW=$(bc <<< "${CURRENT} + ${STEP}")
        ;;
    [dD]*)
        NEW=$(bc <<< "${CURRENT} - ${STEP}")
        ;;
esac

TMPF=$(mktemp)
xrandr --output ${MONITOR} --brightness ${NEW} &> ${TMPF} && \
    notify-send -t 1000 -a BRIGHTNESS -e ${NEW} || \
    notify-send -t 3000 -a BRIGHTNESS -e "ERROR:" "$(cat ${TMPF})"
rm -f ${TMPF}
