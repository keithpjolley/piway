#!/bin/sh
#
# kjolley
# squalor heights, ca, usa
# !date
#
me=$( basename "${0}" )

if [ $(id -u) -ne 0 ]; then
  echo "ERROR: ${me}: Must be root. Goodbye."
  exit 1
fi

mount -o remount,rw /
export PATH="$PATH:/usr/local/bin/"
pihole updateGravity
mount -o remount,ro /
