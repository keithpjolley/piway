#! /usr/bin/python
# -*- coding: UTF8 -*-

from __future__ import print_function

import os, sys
import json
import datetime
import requests

me = os.path.splitext(os.path.basename(sys.argv[0]))[0]
dbintfile = '/usr/local/opt/pirouter/etc/dbint.json'
dhcphosts = "/usr/local/opt/pirouter/tmp_rw/dhcp-hostsfile.txt"

# print to stderr
def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

def myexit(exitcode, *args, **kwargs):
  eprint(*args, **kwargs)
  sys.exit(exitcode)

if not os.geteuid() == 0:
  myexit(1, "{}: {}: {}".format("ERROR", me, "Script must be run as root"))

with open(dbintfile, 'r') as f:
    dbintfo = json.load(f)
url = dbintfo['url'] + '/' +  me

r = requests.post(url, dbintfo)
if(r.status_code != 200):
  myexit(3, "{}: {}: bad https call to '{}'. Expected 200, got: {}".format("ERROR", me, url, r.status_code))

try:
  target = open(dhcphosts, 'w')
  target.truncate()
except IOError:
  myexit(3, "{}: {}: Could not open file '{}' for write: [{}] {}".format("ERROR", me, dhcphosts, e.errno, e.strerror))
except:
  myexit(4, "{}: {}: error opening file {}: {}".format("ERROR", me, dhcphosts, sys.exc_info()[0]))

for values in r.json():
  #print("values: ", end='')
  #print(values)
  target.write("{mac} {hn}\n".format(**values))

target.close()
