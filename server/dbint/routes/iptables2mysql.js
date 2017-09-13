// routes/iptables2mysql.js

// routes named for corresponding programs that need this information.
// this pushes rudimentary bandwidth usage into mysql

// keith p jolley
// Wed Aug  9 12:39:08 PDT 2017

'use strict';
var express  = require('express');
var path     = require('path');
var bcrypt   = require('bcrypt-nodejs');
var mysql    = require('mysql');

var router   = express.Router();

let pidbcnf  = require(path.join(__dirname, '..', 'dbconfig', 'pidbcnf'));
var pirouter = pidbcnf.local.pirouter_ro;
var pibw     = pidbcnf.local.pibw;

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.sendStatus(400);
});

router.post('/', function(req, res, next) {
  
  if(typeof(req.body.username) === 'undefined') {
    console.log("no user");
    res.sendStatus(400);
    return;
  }

  if(typeof(req.body.passwd) === 'undefined') {
    console.log("no passwd");
    res.sendStatus(400);
    return;
  }

  // test that we got good data before making a connection to the db

  // we are expecting an array of data in "iptables"
  if(typeof(req.body.iptables) === 'undefined') {
    console.log("no iptables");
    res.sendStatus(400);
    return;
  }

  if(!Array.isArray(req.body.iptables)) {
    console.log("iptables not an array");
    res.sendStatus(400);
    return;
  }

  // passed an empty data array. could be argued that this is not
  // an error, but, want client to know something went wrong.
  if(req.body.iptables.length < 1) {
    console.log("no iptables data");
    res.sendStatus(400);
    return;
  }

  // now we know we have an iptables array with non-zero length, lets see if there's good data in it
  // note that we get "in" and "out" but our db schema wants "in_eth" and "out_eth"
  let required = ["source", "destination"]
  let integers = ["pkts", "bytes"] // these are required too
  let rename   = ["in", "out"]     // and these are required
  let optional = ["target", "prot", "opt" ];
  let iptables = [];
  
  // make sure we are only injecting colums we know we need.
  req.body.iptables.forEach(function(row) {
    let skip = 0;
    let newrow   = {};
    required.forEach(function(key) {
      if(row.hasOwnProperty(key)) {
        newrow[key] = row[key].substr(0, 24);
      } else {
        skip++;
        console.log("nokey: " + key);
      }
    });
    if(skip === 0) {
      integers.forEach(function(key) {
        if(!row.hasOwnProperty(key) | isNaN(+row[key])) {
          skip++;
          console.log("isNaN: " + key + ", " + row[key]);
        } else {
          newrow[key] = +row[key]; // convert to number
        }
      });
    }
    if(skip === 0) {
      optional.forEach(function(key) {
        switch(key) {
          case "target":
            newrow[key] = row[key].substr(0, 18);
            break;
          case "prot":
          case "opt":
            newrow[key] = row[key].substr(0, 8);
            break;
        }
      })
    }
    if(skip === 0) {
      rename.forEach(function(key) {
        if(row.hasOwnProperty(key)) {
          newrow[key + "_eth"] = row[key].substr(0, 8);
        } else {
          skip++;
          console.log("in/out keys missing: " + key);
        }
      })
    }
    if(skip === 0) {
      iptables.push(newrow);
    }
  });

  let connection = mysql.createConnection(pirouter);

  connection.query("SELECT * FROM users WHERE username = ?", [req.body.username], function(error, results, fields) {
    if(error) {
      console.log("mysql error: " + JSON.stringify(error));
      res.sendStatus(500);
      connection.destroy();
      return;
    }
    if(!results.length) {
      console.log("mysql noresults: " + results.length);
      res.sendStatus(406);
      connection.destroy();
      return;
    }
    if(!bcrypt.compareSync(req.body.passwd, results[0].password)) {
      console.log("bcrypt no compare: (" + req.body.passwd + " != " + results[0].password + ")");
      res.sendStatus(401);
      connection.destroy();
      return;
    }

    let userid = results[0].id;

    connection.end(function(error) {
      if(error) {
        console.log("mysql connection.end() error: " + JSON.stringify(error));
        res.sendStatus(500);
        return;
      }
    });

    let connection2 = mysql.createConnection(pibw);
   
    let sql = "INSERT tsid (ts, delta) SELECT NOW(), TIMESTAMPDIFF(SECOND, MAX(ts), NOW()) FROM tsid";
    connection2.query(sql, function(error, result, fields) {
      if(error) {
        console.log("mysql error: 1. " + JSON.stringify(error));
        res.sendStatus(500);
        connection2.destroy();
        return;
      }
      let id = result.insertId;
      let err = 0;
      
      iptables.forEach(function(row) {
        row['id'] = id;
        connection2.query('INSERT INTO pibw.iptable SET ?', row, function(error, results, fields) {
          if(error) {
            console.log("mysql error: 2. " + JSON.stringify(error));
            err++;
          }
        })
      })
      res.sendStatus((err === 0) ? 200 : 500 );
      connection2.end();
    })
  });
});

module.exports = router;
