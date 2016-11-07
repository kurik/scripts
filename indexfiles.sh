#!/bin/bash

N=$#

printf "%03d" $N

function random {
    printf "%03d" $(( $RANDOM % 1000 ))
}

for i in $@; do
    mv "$i" "$(random)-$i" 
done
