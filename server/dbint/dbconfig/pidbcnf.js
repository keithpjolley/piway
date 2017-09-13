'use strict';

const fs   = require('fs');
const path = require('path');

let remotehost = 'remotedbhostname';

let local  = {
  pirouter_ro: {
    host      : 'localhost',
    user      : 'pirouter_ro',
    password  : '__pirouterropasswd__',
    database  : 'pirouter'
  },
  pirouter_rw : {
    host      : 'localhost',
    user      : 'pirouter_rw',
    password  : '__pirouterrwpasswd__',
    database  : 'pirouter'
  },
  pibw        : {
    host      : 'localhost',
    user      : 'pibw',
    password  : '__pibwpasswd__',
    database  : 'pibw'
  }
};


// put certs in ./mysql-ssl/$remotehost/...
// if you are going to use mysql across the network. but just don't.
let sslcreds   = {
    ca   : fs.readFileSync(path.join(__dirname, 'mysql-ssl', remotehost, 'ca.pem')),
    key  : fs.readFileSync(path.join(__dirname, 'mysql-ssl', remotehost, 'client-key.pem')),
    cert : fs.readFileSync(path.join(__dirname, 'mysql-ssl', remotehost, 'client-cert.pem'))
};

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/assign
let remote = JSON.parse(JSON.stringify(local));

remote.pirouter_ro.host = remotehost;
remote.pirouter_ro.ssl  = sslcreds;
remote.pirouter_rw.host = remotehost;
remote.pirouter_rw.ssl  = sslcreds;

module.exports = {
  'local': local,
  'remote': remote
};
