#!/bin/sh
#
# kjolley
# squalor heights, ca, usa
# Sat Mar  4 12:12:10 PST 2017
#

me=$( basename "${0}" )

date > "/tmp/__________________${me}"

#cd ~pi
#iptables-restore < iptables.all.save
#exit

pidir="/usr/local/opt/pirouter"

if [ ! -d "${pidir}" ]; then
  echo "ERROR: ${me}: no ${pidir}. Goodbye"
  exit 1
fi 

if [ $(id -u) -ne 0 ];then
  echo "ERROR: ${me}: must be root. Goodbye"
  exit 2
fi

export PATH="/usr/local/opt/pirouter/bin:/bin:/usr/bin:/sbin:/usr/local/bin"

homecred="${pidir}/etc/google_cal_credentials.json"
streetcred="${pidir}/tmp_rw/google_cal_credentials.json"

[ -f "${streetcred}" ] || cp "${homecred}" "${streetcred}"

#
# iptables2mysql AND iptablesconfig zero out the rules so be sure to grab stats
# just before reconfig
#

# renable these one at a time
makelocalhosts.py
makedhcphostsfile.py
iptables2mysql.py
wrap_iptablesconfig.sh
pihole restartdns

#
#dediddlealittle.py
