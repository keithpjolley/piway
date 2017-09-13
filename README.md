# pirouter
This project uses iptables to configure a Raspberry Pi as a router. I had a SkyDog router and it 
became a piece of cloud trash when the company no longer supported it. It had a lot of features
I liked that I'm slowly baking into this.

The key features here are parental controls and very severe restrictions on what can access your
network. This is not user friendly at all. I'm slowly adding a UI - for now it's easiest to add/delete
machines to your network via mysql on your server.

Your server should be "in the cloud". I host mine on an ec2 instance. Anywhere you can run Node.js
with access to a database (mysql). I had it on my internal network but that meant your internal
network had to always be on and every outage you had a chicken/egg problem. Your modem should be
serving dhcp which is all your pi's internet facing interface should need to fully configure to
whatever values you have in mysql.

This is an 0.0.1 release. I've gone through the directions for setting up the client a couple times
but I know that's very different than someone new coming into it so I'd appreciate any pointers/help
on how to make the documentation better.

I haven't yet started documentation on the server side but it's actually pretty simple. Create a
mysql using the template. It's probably easiest if you add your hosts with this file too. I have
a "forever" script in /etc/init.d/ that starts up the dbint application and I have an nginx proxy
running.

I'm wanting to finally get this online so sorry this is so brief!  I promise to keep expanding.

Again, please let me know if you find this useful and how to improve.

Keith

p.s.  Current works in progress:
    1. web interface
    2. graphing of bandwidth usage
    3. throttling of bandwidth (I'm very bandwidth constrained - monthly quotas kill me)
    4. documentation!

