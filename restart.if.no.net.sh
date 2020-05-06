#!/bin/bash

# List of peers to check ifup with
PEERS="83.240.0.215 83.240.0.136 8.8.8.8 91.213.160.188"
# How long time in seconds to wait for a peer to response
TOUT=5
# How many times to try when no peer responds
TRIES=15
# How long time in seconds to wait between rounds of peer checks
ROUNDWAIT=60

for try in $(/usr/bin/seq 1 ${TRIES}); do
    for peer in ${PEERS}; do
        if /usr/bin/ping -c 1 -W ${TOUT} ${peer} &>/dev/null; then
            # A peer has responded - let's finish this job
            exit 0
        fi
    done
    sleep ${ROUNDWAIT}
done

# No peer responded during all the rounds. Reboot the universe
/usr/bin/shutdown -r now

exit 1
