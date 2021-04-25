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

function convert2data() {
    local in=$1
    local out=$2
    local text
    local link
    local i=1

    >"${out}"
    while true; do
        ((i++))
        text=$(xmllint --html --noout --noent \
            --xpath "string(//tr[${i}]/td[1]/a[1])" ${in} 2>/dev/null) || return 1
        link=$(xmllint --html --noout --noent \
            --xpath "string(//tr[${i}]/td[1]/a[1]/@href)" ${in} 2>/dev/null) || return 1
        [[ -z "${text}" ]] && break
        
        echo "${text}" "#@#" "${link}" >> "${out}"
    done

    return 0
}

function compare_data() {
    local old="$1"
    local new="$2"
    local l

    # Check for removed records
    while read l; do
        if ! grep -q "${l}" < "${new}"; then
            echo "< ${l}"
        fi
    done < "${old}"

    # Check for added records
    while read l; do
        if ! grep -q "${l}" < "${old}"; then
            echo "> ${l}"
        fi
    done < "${new}"
}

function generate_email() {
    local old="$1"
    local new="$2"
    local old_data=$(mktemp)
    local new_data=$(mktemp)
    local d=$(mktemp)
    local line
    local text
    local link

    CLEANUP="${CLEANUP} ${old_data} ${new_data} ${d}"
    convert2data "${old}" "${old_data}" || return 1
    convert2data "${new}" "${new_data}" || return 1

    #diff -bBwZE ${old_data} ${new_data} | grep -e '< ' -e '> ' > ${d} 
    compare_data ${old_data} ${new_data} > ${d}
    [[ -z "${d}" ]] && return 1

    echo "Subject: ${SUBJECT}"
    echo "To: ${EMAIL}"
    echo "=============== Úřední deska Přibice ==============="
    echo
    echo "Změna na úřední desce: ${URL}"
    echo

    while read status line; do
        text=$(sed 's/#@#.*$//g' <<< "${line}")
        link=$(sed 's/^.*#@#//g' <<< "${line}")
        if [[ "${status}" == ">" ]]; then
            link=${link#"${link%%[![:space:]]*}"} # remove trailing whitespaces
            echo "+ ${text}: ${URL}${link}"
        elif [[ "${status}" == "<" ]]; then
            echo "- ${text}"
        fi
    done < ${d}

    echo
    echo "===================================================="

    rm -f ${old_data} ${new_data} ${d}

    return 0
}

# Make sure cache exists
mkdir -p "${CACHE}" || \
    { echo "Error: Can not access cache at ${CACHE}"; exit 1; }

CF=${CACHE}/deska.html
>>${CF}
TF=$(mktemp)
CLEANUP="${CLEANUP} ${TF}"
curl -k -o ${TF} -s "${URL}" || \
    { echo "Error downloading the edeska at ${URL}"; exit 1; }

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
