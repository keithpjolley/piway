#!/bin/sh
#
# kjolley
# squalor heights, ca, usa
# !date
#

data=/tmp/data.$$
cat<<EOF >"${data}"
{
 "username": "me", 
 "passwd": "passwd"
}
EOF

url="http://localhost:9002/iptablesconfig"

curl -H "Content-Type: application/json" -X POST --data "@${data}" "${url}"
echo ''
[ -f "${data}" ] && rm "${data}"

