#!/bin/bash

# CUPS forgets, from time to time, the list od network browsers.
# This command is to refresh it, so I do not need to remember which service to restart
/usr/bin/sudo /usr/bin/systemctl restart cups-browsed.service

exit $?
#EOF
