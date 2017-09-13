#!/bin/sh
#
# kjolley
# squalor heights, ca, usa
# !date
#
me=$( basename "${0}" )
here=$( dirname "${0}" )

data="${here}/../doodles/iptables2mysql.json"

url="http://localhost:9003/getdata"

curl --trace-ascii - -H "Content-Type: application/json" -X POST --data "@${data}" "${url}"
echo ''

