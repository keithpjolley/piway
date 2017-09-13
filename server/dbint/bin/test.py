#! /usr/bin/env python2.7
# -*- coding: UTF8 -*-

from __future__ import print_function

import requests
import sys, os
import json

me = os.path.basename(sys.argv[0])
#server = 'http://localhost:9002'

def doit(payload, expectthis, path):
  # http://docs.python-requests.org/en/master/user/quickstart/
  url = server + path
  print("trying: " + url)
  r = requests.post(url, json=payload)
  if((r.status_code != expectthis['status']) | (r.reason != expectthis['reason'])):
    print("ERROR!!: ", end='')
  else:
    print("SUCCESS: ", end='')

  print("expected: {}, got: {}. expected: {}, got: {}".format(expectthis['status'], r.status_code, expectthis['reason'], r.reason));

gooddata    = {"username": "me", "passwd": "passwd"}
goodresults = {"status": 200, "reason": "OK"}

# get instead of post - return 400
doit({"sername": "your mom", "key2": "still your mom", "passwd": "your mom!"}, {"status": 400, "reason": "Bad Request"}, '/device')
# no user - return 401
doit({"sername": "your mom", "key2": "still your mom", "passwd": "your mom!"}, {"status": 400, "reason": "Bad Request"}, '/device')
# no passwd - return 401
doit({"username": "your mom", "key2": "still your mom", "passwod": "your mom!"}, {"status": 400, "reason": "Bad Request"}, '/device')
# incorrect passwd - return 401
doit({"username": "k", "key2": "still your mom", "passwd": "your mom!"}, {"status": 401, "reason": "Unauthorized"}, '/device')
# correct username/passwd, empty device - return something
doit({"username": "k", "key2": "still your mom", "passwd": "j"}, {"status": 200, "reason": "OK"}, '/device')
# correct username/passwd, some device - return something
doit(gooddata, goodresults, '/device')
doit(gooddata, goodresults, '/makedhcphostsfile')
doit(gooddata, goodresults, '/makelocalhosts')

baddata = gooddata
doit(baddata, {"status": 400, "reason": "Bad Request"}, '/iptables2mysql') # "gooddata" not good here

baddata['iptables'] = "bad_value"
doit(baddata, {"status": 400, "reason": "Bad Request"}, '/iptables2mysql')

baddata['iptables'] = []
doit(baddata, {"status": 400, "reason": "Bad Request"}, '/iptables2mysql')

gooddata['iptables'] = [
  {
   "bytes": "65930",
   "destination": "0.0.0.0/0",
   "in": "eth1",
   "opt": "--",
   "out": "eth0",
   "pkts": "980",
   "prot": "all",
   "source": "1.2.3.4",
   "target": "ACCEPT"
  },
  {
   "bytes": "12345",
   "destination": "99.99.99.99",
   "in": "eth0",
   "opt": "--",
   "out": "eth1",
   "pkts": "123",
   "prot": "all",
   "source": "0.0.0.0/0",
   "target": "ACCEPT"
  },
  {
   "bytes": "icky bad data",
   "destination": "99.99.99.99",
   "in": "eth0",
   "opt": "--",
   "out": "eth1",
   "pkts": "123",
   "prot": "all",
   "source": "0.0.0.0/0",
   "target": "ACCEPT"
  },
  {
   "bytes": "0",
   "destination": "99.99.99.99-----------------------------------------",
   "in": "eth0---------------------------------------------------",
   "opt": "----------------------------------------------------",
   "out": "eth1-----------------------------------------",
   "pkts": "123",
   "prot": "all-------------------------------------",
   "source": "0.0.0.0/0----------------------------------------",
   "target": "ACCEPT----------------------------------------------"
  }
]

#print(gooddata)

doit(gooddata, goodresults, '/iptables2mysql')
