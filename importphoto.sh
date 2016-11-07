#!/bin/bash

WORKDIR='/store/camera'
GCP='/store/scripts/gcp.py'
GDRIVE='/Pictures/Unin'

for d in "${WORKDIR}"/20[0-9][0-9][0-9][0-9][0-9][0-9]; do
        x=$(basename $d)
        Y=${x:0:4}
        M=${x:4:2}
        D=${x:6:2}
        for f in "$d"/*; do
            echo "${GCP}" -mv -i /root/.gp.json -s /root/.gp "$f" gdrive:"${GDRIVE}"/$Y/$M/$D
        done
done
