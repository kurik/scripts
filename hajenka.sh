#!/bin/bash

URL='https://www.vhajence.com/'
EMAIL=''
SUBJECT="Notifikace: Hájenka"
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

function generate_email() {
    echo "Subject: ${SUBJECT}"
    echo "To: ${EMAIL}"
    echo "=============== Hájenka (Dandi) ==============="
    echo
    echo "Změna na webu Hájenkay: ${URL}"
    echo
    echo "===================================================="

    return 0
}

# Make sure cache exists
mkdir -p "${CACHE}" || \
    { echo "Error: Can not access cache at ${CACHE}"; exit 1; }

CF=${CACHE}/hajenka.html
>>${CF}
TF=$(mktemp)
curl -k -o ${TF} -s "${URL}" || \
    { echo "Error downloading the web at ${URL}"; exit 1; }

if ! diff "${TF}" "${CF}" &> /dev/null; then
    # Make a backup (debug)
    cp "${CF}" "${CF}-$(date '+%Y%m%d-%H%M')"
    # Generate the email body
    BODY=$(generate_email "${CF}" "${TF}")
    # Send an email
    if [[ -n "${EMAIL}" ]]; then
        msmtp -a gmail ${EMAIL} <<< "${BODY}"
    else
        echo "${BODY}"
    fi
fi

mv "${TF}" "${CF}"
