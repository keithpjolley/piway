#!/bin/sh
#
# kjolley
# squalor heights, ca, usa
# Sat May 13 06:58:05 PDT 2017
#
me=$( basename "${0}" )

leasefile="/var/lib/misc/dnsmasq.leases"
leasefile="/usr/local/opt/pirouter/tmp_rw/dhcp.leases"
donothing=0

if [ $(id -u) -ne 0 ]; then
  echo "ERROR: ${me}: must be run as root. Goodbye."
  exit 1
fi

if [ "$1"x = "-nx" ]; then
  donothing=1
  shift
fi

if [ "$#" -ne 1 ]; then
  echo "USAGE: ${me} [-n] 'mac|ipv4|hostname'"
  echo "    Removes lease for the given arg."
  echo "    Stops dnsmasq, removes line(s) from ${leasefile}, starts dnsmasq"
  echo "    -n: dryrun"
  exit 2
fi

echo "INFO: ${me}: Attempting to remove $@ from ${leasefile}"

if [ "$(grep -c "$@" "${leasefile}")" -eq 0 ]; then
  echo "INFO: ${me}: I didn't find '$@' in ${leasefile}"
  echo "INFO: ${me}: Goodbye"
  exit 3
fi

echo "INFO: ${me}: stopping dnsmasq"
if [ "${donothing}" -eq 0 ]; then
  systemctl stop dnsmasq
else
  echo systemctl stop dnsmasq
fi

echo "INFO: ${me}: deleting this:"
sed -n "/$@/p" "${leasefile}"
[ "${donothing}" -eq 0 ] && sed -i "/$@/d" "${leasefile}"

echo "INFO: ${me}: starting dnsmasq"
if [ "${donothing}" -eq 0 ]; then
  systemctl start dnsmasq
else
  echo systemctl start dnsmasq
fi
