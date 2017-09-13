// routes/makelocalhosts.js

// routes named for corresponding programs that need this information.
// this particular information needed for making a local hosts file with all known hosts included

// keith p jolley
// Wed Aug  9 12:39:08 PDT 2017

var express  = require('express');
var path     = require('path');
var bcrypt   = require('bcrypt-nodejs');
var mysql    = require('mysql');

let pidbcnf  = require(path.join(__dirname, '..', 'dbconfig', 'pidbcnf'));
var pirouter = pidbcnf.local.pirouter_ro;

var router  = express.Router();

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
      res.sendStatus(401);
      connection.end();
      return;
    }
    if(!bcrypt.compareSync(req.body.passwd, results[0].password)) {
      console.log("bcrypt no compare: (" + req.body.passwd + " != " + results[0].password + ")");
      res.sendStatus(401);
      connection.end();
      return;
    }

    let userid = results[0].id;

    let sql = "SELECT                       "
            + "   macaddress AS mac,        "
            + "   LCASE(hostname) AS hn     "
            + "FROM devices                 "
            + "WHERE userid = ?             "
            + " AND macaddress IS NOT NULL  "
            + " AND ipv4 IS NOT NULL        "
            + " AND hostname IS NOT NULL    "
            + " AND include                 "
            + "ORDER BY hn";

    connection.query(sql, [userid], function(error, results, fields) {
      if(error) {
        console.log("mysql error.code:  " + error.code);
        console.log("mysql error.errno: " + error.errno);
        console.log("mysql error.sqlMessage: " + error.sqlMessage);
        res.sendStatus(500);
      } else {
        res.json(results);
      }
    })
    connection.end();
  });
});

module.exports = router;
