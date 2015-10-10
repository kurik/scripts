#!/bin/bash

SLEEP=300
TEMPIMG="/tmp/image.png"
IMGTRASHHOLD=32000
GDRIVEPATH="Pictures/Unin"

D=''

while [ 0 ]; do
    # Name of dir to store images
    DIR="$(date +'%Y%m%d')"
    # Filename of the image
    D="$(date +'%Y%m%d-%H%M%S')"
    # Create the directory to store images
    mkdir -p "${DIR}"
    # Go inside the dir-vf flip,mirror
    pushd "${DIR}" && { 
        # Do the snapshot
        fswebcam -r 1280x1024 -S 5 --png 9 --save "${TEMPIMG}"
        # If the image does not contain something useful (detected by image size) do not proceed it
        if [[ $(stat -c '%s' "${TEMPIMG}") -gt ${IMGTRASHHOLD} ]]; then
            # Convert it and store it
            convert -rotate 270 "${TEMPIMG}" "${D}.png"
            # Send the photo to GDrive
            echo "Triggering send of the image to GDrive"
            /store/scripts/importphoto.py -g "${D}.png" "${GDRIVEPATH}" &
        else
            echo "The image ${D}.png is empty ... Ignoring"
        fi
        # Clean up
        rm -f "${TEMPIMG}"
        popd
    }
    # Wait for a while before gou for another snapshots
    echo "Going to sleep for ${SLEEP} seconds"
    sleep ${SLEEP}
done

