#!/bin/bash
bkr distros-list --limit=0 | grep "Name:" | awk "{print \$2}" | sort -u
