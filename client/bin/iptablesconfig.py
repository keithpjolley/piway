#! /usr/bin/env python
# -*- coding: UTF8 -*-
#
# kjolley
# squalor heights, ca, usa
# Sat May  6 08:15:28 PDT 2017
#

# this script creates an iptables configuration shell file
# the output goes to stdout
# the only output going to stdout should be the script file
# "verbose" info needs to go to stderr

from __future__ import print_function

import os
import sys
import json
import socket
import httplib2
import requests

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from dateutil.parser import *
from dateutil.tz import *
from datetime import *

me = os.path.splitext(os.path.basename(sys.argv[0]))[0]
verbose = False
#verbose = True

# print to stderr
def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

def myexit(exitcode, *args, **kwargs):
  eprint(*args, **kwargs)
  sys.exit(exitcode)

# info for google cal
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CALENDAR_ID_FILE   = '/usr/local/opt/pirouter/etc/google_cal_id.txt'
CLIENT_SECRET_FILE = '/usr/local/opt/pirouter/etc/google_cal_secret.json'
CREDENTIALS_FILE   = '/usr/local/opt/pirouter/tmp_rw/google_cal_credentials.json'
APPLICATION_NAME   = 'pirouter'
dbintfile          = '/usr/local/opt/pirouter/etc/dbint.json'

# returns a list of: hostname, mac address, ipv4 address, schedulepolicy
def getdevices():
  # info for pirouter @ jhi
  with open(dbintfile, 'r') as f:
    dbintfo = json.load(f)

  url = dbintfo['url'] + '/' +  me
  r = requests.post(url, dbintfo)
  if(r.status_code != 200):
    myexit(3, "{}: {}: bad https call to '{}'. Expected 200, got: {}".format("ERROR", me, url, r.status_code))
  return r.json()

def getvalidpolicies(devices):
  policies = []
  for device in devices:
    if device["policy"] not in policies:
      policies.append(device["policy"])
  return policies

def between(start, now, end):
  return (start <= now < end)

def getcredentials():
  """Gets valid user credentials from storage.
  If nothing has been stored, or if the stored credentials are invalid,
  the OAuth2 flow is completed to obtain the new credentials.
  Returns:
      Credentials, the obtained credential.
  """
  credential_path = CREDENTIALS_FILE
  store = Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    credentials = tools.run_flow(flow, store)
  return credentials

def getcurrentpolicies(now, validpolicies):
  currentpolicies = []
  credentials = getcredentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http)
  # get all calendar events from midnight last night to midnight tonight
  midnight = datetime.combine(date.today(), time())
  timeMin  = midnight.isoformat() + 'Z'
  timeMax  = (midnight + timedelta(days=1)).isoformat() + 'Z'
  if(verbose): eprint("{}: {}: {}".format("INFO", me, "Retrieving current policies from Google Calendar"))
  eventsResult = service.events().list(
      calendarId='7ijel4tivg299i2tol5v0mqv2k@group.calendar.google.com',
      timeMin=timeMin, timeMax=timeMax, singleEvents=True
    ).execute()
  events = eventsResult.get('items', [])
  if not events:
    eprint('{}: No local policies defined. Nothing for me to do.'.format(me))
    sys.exit(0)
  for event in events:
    # don't bother parsing if no description field
    if 'description' in event:
      # get start and end times of the calendar event
      start = parse(event['start'].get('dateTime', event['start'].get('date')))
      end   = parse(event['end'].get('dateTime', event['end'].get('date')))
      # if no tzinfo that means it's an all day event and is "on"
      # otherwise, is the policy currently in effect?
      if ((start.tzinfo is None) or between(start, now, end)):
        policy = event['description'].lower()
        # don't process if i've already collected this policy
        if policy not in currentpolicies:
          if policy not in validpolicies:
            if(verbose): eprint("INFO: {}: Ignoring policy '{}' because no devices use it.".format(me, policy))
          else:
            currentpolicies.append(policy)
  return currentpolicies

# prints the header
def header():
  head = '''#!/bin/sh

# do not manually edit. automatically created by ${me}
# this file created at (timestamp not included because it borks it all up. run 'ls -l'.)

echo "INFO: ${0}: updating iptables."

# flush anything in the system
iptables --flush
iptables --delete-chain
iptables --flush FORWARD
iptables --table nat --flush
iptables --table nat --delete-chain

#iptables --table nat -A POSTROUTING -o eth0 -j MASQUERADE
#exit

# if all we are doing is cleaning up, we are done.
[ -n "${1}" -a "${1}" = "--off" ] && exit

## assume this is already done. ro filesystem.
## echo 1 > /proc/sys/net/ipv4/ip_forward
## sed -i.bak '/\(^net.ipv4.ip_forward=\)\(0\)/{s//#\\1\\2\\n\\11/;}' 

## create policies
iptables --policy INPUT   DROP
iptables --policy OUTPUT  DROP
iptables --policy FORWARD DROP

# don't forward any dns queries
##kj##iptables -A FORWARD -p udp --destination-port domain -j REJECT

#####################################################################################////////////////////////////////
#####################################################################################////////////////////////////////
#####################################################################################////////////////////////////////
#####################################################################################////////////////////////////////
#iptables --append FORWARD --in-interface eth1 --out-interface eth0 --source 192.168.99.200      --jump ACCEPT
#iptables --append FORWARD --in-interface eth0 --out-interface eth1 --destination 192.168.99.200 --jump ACCEPT
#####################################################################################////////////////////////////////
#####################################################################################////////////////////////////////
#####################################################################################////////////////////////////////
#####################################################################################////////////////////////////////


###
##
# allow outbound from mac addresses we know (this next section is automated)
'''
  print(head)

def footer():
  foot='''#
# end of "policy" based section
#
##
###

# allow inbound for anything with an existing connection
#iptables --append FORWARD --in-interface eth0 --out-interface eth1 --match state --state RELATED,ESTABLISHED --jump ACCEPT

# any hosts not listed above send to the bit bucket. this makes it impossible for hosts i don't know about to connect to
# the internet
# edit this file: $mac_addrs 
# to add new hosts to the network
# edit this file: $policies
# to change when the host can connect to the internet

# Allow unlimited traffic on loopback
iptables --append INPUT  --in-interface  lo --jump ACCEPT
iptables --append OUTPUT --out-interface lo --jump ACCEPT

# Allow unlimited traffic within LAN
iptables --append INPUT  --in-interface  eth1 --jump ACCEPT
iptables --append OUTPUT --out-interface eth1 --jump ACCEPT

# Allow unlimited traffic to/from modem
iptables --append INPUT  --in-interface  eth0 --match mac --mac-source 00:80:AE:4B:79:46 --jump ACCEPT
iptables --append OUTPUT --out-interface eth0 --jump ACCEPT

# turn NAT on on outgoing traffic
iptables --table nat --append POSTROUTING --out-interface eth0 --jump MASQUERADE

# END'''
  print(foot)
    
def main():
  now = datetime.now(tzutc())
  devices = getdevices()
  relevantpolicies = getvalidpolicies(devices) 
  currentpolicies  = getcurrentpolicies(now, relevantpolicies)
  header()
  # main loop
  for device in sorted(devices, key=lambda item: socket.inet_aton(item['ipv4'])):
    if device["policy"] in currentpolicies:
      print('# {} {} {} -- incoming OK'.format(device['hn'], device['ipv4'], device['policy']))
      print('iptables --append FORWARD --in-interface eth1 --out-interface eth0 --source {}      --jump ACCEPT'.format(device['ipv4']))
      print('iptables --append FORWARD --in-interface eth0 --out-interface eth1 --destination {} --jump ACCEPT'.format(device['ipv4']))
      print('')
  footer()

if __name__ == '__main__':
  main()













