#!/bin/bash

DEVICE_IP="172.16.2.199"
DEVICE="net:${DEVICE_IP}:pixma"
RESOLUTION=300
MODE="Color"
OUTFILE="scan.pdf"
VERBOSE=""

SCRIPT="${0}"

function help() {
    echo "$SCRIPT [-d DEVICE] [-ip IPADDRESS] [-r RESOLUTION] [-m MODE] [-v] [-h] [OUTFILE]"
    echo "  -d DEVICE ... scaner device. The default is ${DEVICE}"
    echo "  -ip IPADDRESS ... IP address of the scaner. The default is ${DEVICE_IP}"
    echo "  -r RESOLUTION ... Resolution of the scanner in DPI. The possible values are 150/300/600. The default is ${RESOLUTION} dpi"
    echo "  -m MODE ... Color mode. Possible values are Color/Gray/Lineart. the default is ${MODE}"
    echo "  -v ... be verbose"
    echo "  -h ... print help message and exits"
    echo "  OUTFILE ... The output file. The default is ${OUTFILE}"
}

# Check dependencies
type -t gm &> /dev/null || { echo "ERROR: GraphicsMagick is not installed."; exit 1; }
type -t scanimage &> /dev/null || { echo "ERROR: sane-backends is not installed."; exit 1; }

# Parse cmdline
while [[ $# > 0 ]]; do
    case ${1} in
        "-d")
            [[ $# > 1 ]] || { echo "ERROR: Missing DEVICE parameter"; exit 1; }
            DEVICE="${2}"
            shift
            ;;
        "-ip")
            [[ $# > 1 ]] || { echo "ERROR: Missing IPADDRESS parameter"; exit 1; }
            DEVICE_IP="${2}"
            DEVICE="net:${DEVICE_IP}:pixma"
            shift
            ;;
        "-r")
            echo $#
            [[ $# > 1 ]] || { echo "ERROR: Missing RESOLUTION parameter"; exit 1; }
            case ${2} in
                150)
                    RESOLUTION=150
                    ;;
                300)
                    RESOLUTION=300
                    ;;
                600)
                    RESOLUTION=600
                    ;;
                *)
                    echo "ERROR: Invalid resolution >>${2}<<"
                    help
                    exit 1
                    ;;
            esac
            shift
            ;;
        "-m")
            [[ $# > 1 ]] || { echo "ERROR: Missing MODE parameter"; exit 1; }
            case ${2} in
                Color)
                    MODE=Color
                    ;;
                Gray)
                    MODE=Gray
                    ;;
                Lineart)
                    MODE=Lineart
                    ;;
                *)
                    echo "ERROR: Invalid mode >>${2}<<"
                    help
                    exit 1
                    ;;
            esac
            shift
            ;;
        -v|--verbose)
            VERBOSE="-v"
            ;;
        -h|--help)
            help
            exit 0
            ;;
        -*)
            echo "ERROR: Invalid parameter >>${1}<<"
            help
            exit 1
            ;;
        *)
            OUTFILE="${1}"
            ;;
    esac
    shift
done

if [[ -n "${VERBOSE}" ]]; then
    echo DEVICE_IP: ${DEVICE_IP}
    echo DEVICE: ${DEVICE}
    echo RESOLUTION: ${RESOLUTION}
    echo MODE: ${MODE}
    echo OUTFILE: ${OUTFILE}
fi

# Run the scanning
scanimage ${VERBOSE} -d "${DEVICE}" --resolution "${RESOLUTION}" --mode "${MODE}" | gm convert - "${OUTFILE}"
