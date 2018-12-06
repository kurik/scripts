#!/bin/sh

ADDRS="83.240.118.129 83.240.0.214 83.240.0.135 8.8.8.8"
#ADDRS="83.240.118.1"

for addr in ${ADDRS}; do
    if ping -c 1 $addr 2>&1 >/dev/null; then
        exit 0
    fi
done

/sbin/reboot

exit 1
#EOF
