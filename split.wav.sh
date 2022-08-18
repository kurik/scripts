#!/bin/bash

LIST='./list'
ODIR='./out'
OEXT="mp3"

mkdir -p "${ODIR}"

#sox infile.wav output.wav trim 0 30

# read the list file
while read tstart index name; do
    tstart=$(tr -d '[]' <<< ${tstart})
    if [[ "${tstart}" == "00:00:00" ]]; then
        A="${tstart}"
        I=$(tr -d '.' <<< ${index})
        N=$(sed -e 's/ - /-/g' -e 's/  */ /g' -e 's/ /./g' \
            -e 's/\//./g' -e 's/\.\.*/./g' <<< "${name}")
        continue
    else
        B=${tstart}
        sox "$1" "${ODIR}/${I}-${N}.${OEXT}" trim "${A}" "=${B}"

        A="${B}"
        I=$(tr -d '.' <<< ${index})
        N=$(sed -e 's/ - /-/g' -e 's/  */ /g' -e 's/ /./g' \
            -e 's/\//./g' -e 's/\.\.*/./g' <<< "${name}")
    fi
done < ${LIST}

sox "$1" "${ODIR}/${I}-${N}.${OEXT}" trim "${A}" "-0"
