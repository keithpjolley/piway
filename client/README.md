#HOW TO CREATE THE PI ROUTER.

This is a router, gateway, dns server, ad blocker, dhcp server, and soon-to-be vpn server.

##PHYSICAL SETUP:
  1. An original model RPi with a 4GB SD card. I don't think this is important
  2. eth0 (builtin) connects to modem - uses dhcp from modem
  3. eth1 (usb dongle) connects to lan `ip: 192.168.99.1    bcast:192.168.99.255  mask:255.255.255.0`
 
Your network probably does not look like this. The config for eth0 is from dhcp. It changes.


##MAKE BOOT DRIVE:
I used the 2017-01-11-raspbian-jessie-lite.img image and copied it to the SD card
from another RPi. Be careful that your "of" target is set correctly.
```$ dd bs=4096 of=/dev/rdiskN if=2017-01-11-raspbian-jessie-lite.img```  

Boot the RPi using the SD card you just imaged and login. Default account is "pi", passwd "raspberry".

```
% sudo apt-get -y update
% sudo apt-get -y upgrade
% sudo reboot
% echo 'raspi-config: set expand filesystem, locale, timezone, keyboard, hostname, set passwd, turn on sshd'
% echo 'raspi-config: update raspi-config'
% sudo raspi-config
% echo 'set root password'
% sudo passwd
% ssh-keygen
% ssh-copy-id "user@somewhere"
% sudo apt-get -y install bc locate rsync vim vim-doc vim-scripts indent telnet tcpdump python-pip
# this comments out the last 4 lines of rsyslog.conf. not sure why anyone thought this was a good idea.
% sudo sed -i.org "$(echo "$(echo $(wc -l< /etc/rsyslog.conf)-3|bc),$(wc -l< /etc/rsyslog.conf )")"'s/^/# -\_- #/' /etc/rsyslog.conf
% sync;sync;sync;sudo shutdown -r now
% sudo apt-get -y update       && \
  sudo apt-get -y upgrade      && \
  sudo apt-get -y dist-upgrade && \
  sudo apt-get -y autoclean    && \
  sudo apt-get -y autoremove
% (echo 'nameserver 208.67.222.123';echo 'nameserver 208.67.220.123') | sudo tee /etc/resolv.conf

## get networking ready to NAT
% sudo sysctl -w net.ipv4.ip_forward=1
% sudo sed -i.bak '/\(^net.ipv4.ip_forward=\)\(0\)/{s//#\1\2\n\11/;};s/^#\(net.ipv4.ip_forward=1\)/#\1\n\1/;' /etc/sysctl.conf

## try making filesystem readonly: http://petr.io/en/blog/2015/11/09/read-only-raspberry-pi-with-jessie/

% sudo apt-get -y remove --purge dphys-swapfile logrotate triggerhappy
% sudo apt-get -y install busybox-syslogd
% sudo apt-get -y autoremove --purge
% sudo dpkg --purge rsyslog


Edit add "fastboot noswap ro" to the end of the first line of /boot/cmdline.txt.
-- 'fastboot' caused the RPi to not boot. Removed 'fastboot' and it works fine. --
% sudo sed -i 's/\(.*\)/\1 fastboot noswap ro/;1q' /boot/cmdline.txt   #*

% sudo rm -rf /var/lib/dhcp/ /var/run /var/spool /var/lock /etc/resolv.conf
% sudo ln -s /tmp /var/lib/dhcp
% sudo ln -s /tmp /var/run
% sudo ln -s /tmp /var/spool
% sudo ln -s /tmp /var/lock
% sudo touch /tmp/dhcpcd.resolv.conf; sudo ln -s /tmp/dhcpcd.resolv.conf /etc/resolv.conf
% sudo vi /usr/lib/tmpfiles.d/var.conf
-- change 'd /var/spool 0755 - - -'
-- to     'd /var/spool 1777 - - -'

% sudo vi /etc/fstab
# http://petr.io/en/blog/2015/11/09/read-only-raspberry-pi-with-jessie/
tmpfs /tmp                           tmpfs   nosuid,nodev         0  0
tmpfs /var/log                       tmpfs   nosuid,nodev         0  0
tmpfs /var/tmp                       tmpfs   nosuid,nodev         0  0
tmpfs /var/lib/misc                  tmpfs   nosuid,nodev         0  0 
tmpfs /usr/local/opt/pirouter/tmp_rw tmpfs   nosuid,nodev         0  0

# a swapfile is not a swap partition, no line here
#   use  dphys-swapfile swap[on|off]  for that

This keeps vi from complaining about not being able to write ~/.viminfo.
Don't worry about it if you don't use vi(m)
% sudo vi /etc/vim/vimrc.local
"
" change where ~/.viminfo is written because we are on a ro filesystem
" http://vimdoc.sourceforge.net/htmldoc/options.html#'viminfo'
" could just as well eliminate, but let's try this. 
"
:set viminfo='100,n/tmp/.viminfo.${USER}

Update ntp.conf to use a rw filesystem
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


## this no longer is required since moving to http!
## install python mysql connector
Oracle makes installing this much more of a pain in the ass than it needs to be.
See here. https://dev.mysql.com/downloads/connector/python/
I downloaded 'mysql-connector-python_2.1.6-1debian8.2_all.deb'

% sudo dpkg -i ./mysql-connector-python_2.1.6-1debian8.2_all.deb

Be aware:

% /usr/bin/pip --version
pip 1.5.6 from /usr/lib/python2.7/dist-packages (python 2.7)
% /usr/local/bin/pip --version
pip 9.0.1 from /usr/local/lib/python2.7/dist-packages (python 2.7)





Install required python modules
% sudo pip install httplib2 apiclient discovery

Set the dhcp lease file to a rw filesystem  (needs to be done after pihole upgrades too)
% sed 's%^\(dhcp-leasefile=.*\)%#\1\ndhcp-leasefile=/var/tmp/dhcp.leases%' /etc/dnsmasq.d/02-pihole-dhcp.conf  #*

Before running pihole install make sure you know which is going to be your 
public interface (wan network port connected to modem) and your private 
interface (lan port connected to your internal network). On mine, eth0
is the builtin port and I use it to connect to the modem (wan).

Make sure the dhcp server is pointing at the correct ethers file:
% grep dhcp-hostsfile /etc/dnsmasq.d/01-pihole.conf
dhcp-hostsfile=/usr/local/opt/pirouter/tmp_rw/dhcp-hostsfile.txt

# pihole installs the dns and dhcp servers that we need

## Install pihole. Use defaults as we put in our saved config next step.
Be sure your ethernet dongle is plugged in before running this next command
% curl -sSL https://install.pi-hole.net | bash

Let it install all the required packages. When it asks "Choose an Interface",
pick the "lan/internal" port that matches the "eth0/eth1" scheme in the "Physical Setup" section above.

Upstream provider - use which ever you want. I use the following "Custom" DNS servers:
Family Shield: https://www.opendns.com/setupguide/?url=familyshield
OpenDNS Family Shield DNS IP addresses: 208.67.222.123, 208.67.220.123

I block ads on IPv4 & IPv6

Choose whatever IPv4 address/network you want. I use 192.168.99.1/24 (netmask: 255.255.255.0)

This *is* the gateway so the gateway's IP address is the same as above.


with the filesystem in "rw" mode:
% sudo pihole -a -p 'My Password'   # this gets reset with config sync
//% sudo vi /etc/dnsmasq.conf
//to include the following (match your network to what you chose above) in the appropriate places:


% sudo vi /etc/dnsmasq.d/01-pihole.conf
addn-hosts=/usr/local/opt/pirouter/tmp_rw/hosts.local
log-facility=/var/log/pihole.log
dhcp-range=192.168.99.50,192.168.99.99,1h
dhcp-range=1234::2, 1234::500, 64, 1h


Notice that the IPv4 dhcp-range is from .50 to .99.
All my reserved ip addresses are from .100 to .254. 
This is to help me keep track of what's on the network
and helps prevent a device that's not known to me from
getting an ip address that should be reserved (and making
it out of the network). It also makes it a lot easier to
find new devices on the network using "arp -a".


PiHole creates /etc/cron.d/pihole which is destined to fail on "ro" filesystem. Help it out.

% cat # use /bin/sh to run commands, no matter what /etc/passwd says
SHELL=/bin/sh

# run pirouter at boot
@reboot root /usr/local/opt/pirouter/bin/routerrulesupdate.sh

# run pirouter update every five minutes
*/5 * * * *   root /usr/local/opt/pirouter/bin/routerrulesupdate.sh      #*

# udpate pihole data once a week
@weekly root /usr/local/opt/pirouter/bin/updatePiHole.sh





## cleanup
No matter what I try pihole config really just wants to config eth0 as the internal interface.
Here's a way to clean up those mistakes:
% sudo vi $(grep -rl 192.168.99.1 /etc)
^^ change all occurances of eth0 to eth1 and reboot.

Go to the admin web interface: 192.168.99.1/admin
Password is what you set it to a few lines up.
Go to the "Settings" tab. Enable "Pi-hole DHCP server"









Script to enable update of pihole:
% cat /usr/local/opt/pirouter/bin/updatePiHole.sh
#!/bin/sh
#
# kjolley
# squalor heights, ca, usa
# Thu May 18 08:54:21 PDT 2017
#
me=$( basename "${0}" )

if [ $(id -u) -ne 0 ]; then
  echo "ERROR: ${me}: Must be root. Goodbye."
  exit 1
fi

mount -o remount,rw /
export PATH="$PATH:/usr/local/bin/"
pihole updateGravity
mount -o remount,ro /





Enable lighttpd to run on "ro" filesystem
$ cat external.conf
# /etc/lighttpd/external.conf
server.errorlog-use-syslog = "enable" 
accesslog.use-syslog       = "enable"


Point the dhcp.leases file to rw filesystem.
I use /usr/local/opt/pirouter/tmp_rw/dhcp.leases
% sudo vi $(grep -rl dhcp.leases /etc)

Make sure dnsmasq is authoritative dhcp server:
% grep '^dhcp-authoritative' /etc/dnsmasq.conf
dh


# change location of pihole-FTL.db file to rw filesystem
% cd /tmp; git clone https://github.com/pi-hole/FTL.git; cd FTL
% vi struct.h
change /etc/pihole/pihole-FTL.db to /var/tmp/pihole-FTL.db or somesuch
% make && make install
% sudo /etc/init.d/pihole-FTL restart











Notes below.  Ignore.




ENABLE THE bandwidth monitor :

# point my.cnf to the mysql database of your choice. i run mine NOT on the pi.
% cat my.cnf
[client]
user=pibw
host=remote.mysql.server.host
database=pibw
password=__mypasswd__
% cat makedb.msql
CREATE DATABASE IF NOT EXISTS pibw;
USE pibw;

# here's sample input.  i don't care about the stuff out past the "destination" column
# pkts bytes target     prot opt in     out     source               destination         
# 0        0 ACCEPT     all  --  eth1   eth0    192.168.99.101       0.0.0.0/0           
# 0        0 ACCEPT     all  --  eth0   eth1    0.0.0.0/0            192.168.99.101       state RELATED,ESTABLISHED

# not sure yet how to index, or if i will need to. optimize later.
DROP TABLE IF EXISTS iptable;
CREATE TABLE IF NOT EXISTS iptable (
  ts          DATETIME DEFAULT CURRENT_TIMESTAMP,
  pkts        INT      UNSIGNED NOT NULL,
  bytes       BIGINT   UNSIGNED NOT NULL,
  target      VARCHAR(18)       NOT NULL,
  prot        VARCHAR(8)        NOT NULL,
  opt         VARCHAR(8)        NOT NULL,
  in_eth      VARCHAR(8)        NOT NULL,
  out_eth     VARCHAR(8)        NOT NULL,
  source      VARCHAR(24)       NOT NULL,
  destination VARCHAR(24)       NOT NULL,
  UNIQUE (ts, source, destination)
);

CREATE USER 'pibw'@'localhost' IDENTIFIED BY '__mypasswd__';
CREATE USER 'pibw'@'%' IDENTIFIED BY '__mypasswd__';
GRANT SELECT, INSERT on pibw.* to 'pibw'@'localhost';
GRANT SELECT, INSERT on pibw.* to 'pibw'@'%';

