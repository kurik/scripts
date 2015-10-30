#!/bin/bash

function help {
    echo "Usage:"
    echo "      $0 command"
    echo
    echo "Available commands:"
    echo "  upgrade ... perform upgrade of all pip modules"
    echo "  clean   ... clean the PIP cache"
}

case "${1}" in
    "upgrade")
        pip3 freeze --local | \
            grep -v '^\-e' | \
            cut -d = -f 1  | \
            xargs -n1 pip3 install -U
        ;;
    "clean")
        rm -rf ~/.pip/*
        rm -rf ~/.cache/pip
        ;;
    *)
        echo "ERROR: Unknown command" >&2
        echo >&2
        help >&2
        exit 1
        ;;
esac

