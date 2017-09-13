#! /usr/bin/env python
# -*- coding: UTF8 -*-

import httplib, urllib
import sys, os

me = os.path.basename(sys.argv[0])

server = 'localhost:9002'
path   = '/device'
user   = 'me'
passwd = 'passwd'

params = urllib.urlencode({'username': user, 'passwd': passwd})
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
conn = httplib.HTTPConnection(server)
conn.request("POST", "/device", params, headers)

response = conn.getresponse()
print response.status, response.reason
data = response.read()
print data
conn.close()

