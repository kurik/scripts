#!/bin/bash

LAYOUTS="us cz:qwerty"
STATUSF="${HOME}/.cache/switchkeyboard.status"

# Get the current status
CURRENT=$([[ -r ${STATUSF} ]] && cat ${STATUSF} || echo "${LAYOUTS%% *}")

# Get the first item in the list
# ${LAYOUTS%% *}
#
# Get remaining items in the list
# ${LAYOUTS#* }

function get_next_layout() {
  local current="${1%%:*}"
  local layouts="$2"
  local l="${layouts} "

  while [[ "${l%% *}" != "${current}" ]]; do
    l="${l#* }"
    [[ -z "${l}" ]] && { echo "${layouts%% *}"; return; }
  done
  l="${l#* }"
  [[ -n "${l}" ]] && { echo ${l%% *}; return; }
  echo ${layouts%% *}
}

CURRENT=$(get_next_layout "${CURRENT}" "${LAYOUTS}")
setxkbmap ${CURRENT//:/ }

# Save the current status
echo "${CURRENT}" > ${STATUSF}

# Switch flag in try if available
YAD="/usr/bin/yad"
FLAGDIR="/home/jkurik/Pictures/"
FLAGPID="${HOME}/.cache/flag.pid"
FLAGIMG="${FLAGDIR}/${CURRENT%%:*}-flag.png"
if [[ -x "${YAD}" && -r "${FLAGIMG}" ]]; then
  # Kill the old flag
  [[ -r "${FLAGPID}" ]] && kill $(cat "${FLAGPID}") &>/dev/null
  yad --notification --image="${FLAGIMG}" &
  echo $! > "${FLAGPID}"
fi
