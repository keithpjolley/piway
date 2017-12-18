#!/bin/sh
#
# kjolley
# squalor heights, ca, usa
# !date
#

# "temporary" while I put this functionality into iptablesconfig.py

me=$( basename "${0}" )

export PATH=/usr/local/opt/pirouter/bin:/bin:/usr/bin:/sbin:/usr/sbin

tmp="/usr/local/opt/pirouter/tmp_rw"
new="${tmp}/iptablesconfig.new.sh"
old="${tmp}/iptablesconfig.old.sh"

[ -f "${new}" ] && mv "${new}" "${old}"
touch "${old}"

iptablesconfig.py > "${new}"
stat="$?"

if [ "${stat}" -ne 0 ]; then
  echo "ERROR: ${me} exited with status: ${stat}"
  exit "${stat}"
fi

# Has the configuration changed AND do we have a currently valid config?
# If so, nothing to do. Goodbye.
diff "${new}" "${old}" > /dev/null && [ "$(iptables --list | wc -l)" -gt 8 ] && exit

sh "${new}"
