#!/bin/bash

while ! wget --no-netrc --no-use-server-timestamps -T 5 --no-proxy --prefer-family=IPv4 -c "${X}"; do sleep 1; done

return $?
