#!/bin/bash

find "$1" -type f | while read i; do
    if cp "$i" "$i".refresh; then
        mv "$i".refresh "$i"
    else
        rm -f "$i".refresh
    fi
done
