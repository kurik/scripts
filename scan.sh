#!/bin/bash

DEVICE_IP="172.16.2.199"
DEVICE="net:${DEVICE_IP}:pixma"
RESOLUTION=300
MODE="Color"
OUTFILE="scan.pdf"

scanimage -d "${DEVICE}" --resolution "${RESOLUTION}" --mode "${MODE}" | gm convert - "${OUTFILE}"
