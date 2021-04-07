#!/bin/bash

URL='http://www.edeska.cz/pribice/'
EMAIL=''
SUBJECT="Notifikace: Úřední deska Přibice"
CACHE=~/.cache/$(basename "$0")/
NOTIFY=

function usage() {
    echo "Usage:"
    echo "$0 [-u <url>] [-s <text>] <email address>"
    echo "   -u|--url"
    echo "      ... url to the uredni deska (default is ${URL})"
    echo "   -s|--subject"
    echo "      ... Subject of the notifcation email"
    echo "   <email address>"
    echo "      ... email address to send the notification to if there is a change"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
      '-u'|'--url')
        shift
        URL="$1"
        ;;
      '-s'|'--subject')
        shift
        SUBJECT="$1"
        ;;
      *)
        EMAIL="$1"
        ;;
    esac
    shift
done

BODY="Subject: ${SUBJECT}
To: ${EMAIL}
=============== Úřední deska Přibice ===============

Změna na úřední desce: ${URL}

====================================================
"

# Make sure cache exists
mkdir -p "${CACHE}" || \
    { echo "Error: Can not access cache at ${CACHE}"; exit 1; }

CF=${CACHE}/deska.html
TF=$(mktemp)
curl -k -o ${TF} -s "${URL}" || \
    { echo "Error downloading the edeska at ${URL}"; exit 1; }

if [[ -f "${CF}" ]]; then
    if diff "${TF}" "${CF}" &> /dev/null; then
      NOTIFY=no
    fi
fi
[[ -z "${NOTIFY}" ]] && msmtp -a gmail ${EMAIL} <<< "${BODY}"
mv "${TF}" "${CF}"
