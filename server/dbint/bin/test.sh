#!/bin/sh
#
# kjolley
# squalor heights, ca, usa
# !date
#

data=/tmp/data.$$
cat<<EOF >"${data}"
{
 "username": "myname", 
 "passwd": "mypasswd", 
 "iptables": [
  {
   "opt": "--", 
   "destination": "0.0.0.0/0", 
   "target": "ACCEPT", 
   "prot": "all", 
   "bytes": "40", 
   "source": "192.168.99.153", 
   "in": "eth1", 
   "pkts": "1", 
   "out": "eth0"
  }, 
  {
   "opt": "--", 
   "destination": "192.168.99.153", 
   "target": "ACCEPT", 
   "prot": "all", 
   "bytes": "40", 
   "source": "0.0.0.0/0", 
   "in": "eth0", 
   "pkts": "1", 
   "out": "eth1"
  }, 
  {
   "opt": "--", 
   "destination": "0.0.0.0/0", 
   "target": "ACCEPT", 
   "prot": "all", 
   "bytes": "40", 
   "source": "192.168.99.179", 
   "in": "eth1", 
   "pkts": "1", 
   "out": "eth0"
  }, 
  {
   "opt": "--", 
   "destination": "192.168.99.179", 
   "target": "ACCEPT", 
   "prot": "all", 
   "bytes": "40", 
   "source": "0.0.0.0/0", 
   "in": "eth0", 
   "pkts": "1", 
   "out": "eth1"
  }, 
  {
   "opt": "--", 
   "destination": "0.0.0.0/0", 
   "target": "ACCEPT", 
   "prot": "all", 
   "bytes": "2433", 
   "source": "192.168.99.200", 
   "in": "eth1", 
   "pkts": "35", 
   "out": "eth0"
  }, 
  {
   "opt": "--", 
   "destination": "192.168.99.200", 
   "target": "ACCEPT", 
   "prot": "all", 
   "bytes": "10358", 
   "source": "0.0.0.0/0", 
   "in": "eth0", 
   "pkts": "34", 
   "out": "eth1"
  }, 
  {
   "opt": "--", 
   "destination": "0.0.0.0/0", 
   "target": "ACCEPT", 
   "prot": "all", 
   "bytes": "3934", 
   "source": "192.168.99.201", 
   "in": "eth1", 
   "pkts": "60", 
   "out": "eth0"
  }, 
  {
   "opt": "--", 
   "destination": "192.168.99.201", 
   "target": "ACCEPT", 
   "prot": "all", 
   "bytes": "5464", 
   "source": "0.0.0.0/0", 
   "in": "eth0", 
   "pkts": "61", 
   "out": "eth1"
  }
 ]
}
EOF


curl -H "Content-Type: application/json" -X POST --data "@${data}" http://localhost:9002/iptables2mysql;
echo ''
[ -f "${data}" ] && rm "${data}"

