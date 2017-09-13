#! /usr/bin/python
# -*- coding: UTF8 -*-

#
# Create a hosts file for the local network for dnsmasq to serve
# This needs to get gathered from 'the cloud' - not mysql.
#
# Keith Jolley
# Sun Jun 11 04:46:44 PDT 2017
# v2. Wed Aug  9 13:19:41 PDT 2017  // from mysql to html
# Squalor Heights, Jamul, CA
#

from __future__ import print_function

import os, sys
import json
import requests
import datetime

me = os.path.splitext(os.path.basename(sys.argv[0]))[0]

# print to stderr
def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

def myexit(exitcode, *args, **kwargs):
  eprint(*args, **kwargs)
  sys.exit(exitcode)

if not os.geteuid() == 0:
  myexit(1, "{}: {}: {}".format("ERROR", me, "Must be run as root."))

hostsfile  = "/usr/local/opt/pirouter/tmp_rw/hosts.local"
headerfile = "/usr/local/opt/pirouter/etc/hosts.header"
dbintfile  = "/usr/local/opt/pirouter/etc/dbint.json"

with open(dbintfile, 'r') as f:
  dbintfo = json.load(f)
url = dbintfo['url'] + '/' +  me
r = requests.post(url, dbintfo)
if(r.status_code != 200):
  myexit(3, "{}: {}: bad https call to '{}'. Expected 200, got: {}".format("ERROR", me, url, r.status_code))

headerf = open(headerfile, "r")
header  = headerf.read()   # even for the pi this *should* be small
headerf = headerf.close()

try:
  target = open(hostsfile, 'w')
  target.truncate()
except IOError:
  myexit(3, "{}: {}: Could not open file '{}' for write: [{}] {}".format("ERROR", me, hostsfile, e.errno, e.strerror))
except:
  myexit(4, "{}: {}: error opening file {}: {}".format("ERROR", me, hostsfile, sys.exc_info()[0]))

target.write(header.format(me, datetime.datetime.now(), headerfile, ""))

for values in r.json():
  target.write("{ipv4} {hn} {hn}.local\n".format(**values))

target.close()
