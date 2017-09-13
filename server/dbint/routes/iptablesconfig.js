// routes/makelocalhosts.js

// routes named for corresponding programs that need this information.
// this particular information needed for making a local hosts file with all known hosts included

// keith p jolley
// Wed Aug  9 12:39:08 PDT 2017

var express  = require('express');
var path     = require('path');
var bcrypt   = require('bcrypt-nodejs');
var mysql    = require('mysql');

var router   = express.Router();

let pidbcnf  = require(path.join(__dirname, '..', 'dbconfig', 'pidbcnf'));
var pirouter = pidbcnf.local.pirouter_ro;

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.sendStatus(400);
});

router.post('/', function(req, res, next) {

  if(typeof(req.body.username) === 'undefined') {
    console.log("no user");
    res.sendStatus(400);
  }

  if(typeof(req.body.passwd) === 'undefined') {
    console.log("no passwd");
    res.sendStatus(400);
  }

  let connection = mysql.createConnection(pirouter);

  connection.query("SELECT * FROM users WHERE username = ?", [req.body.username], function(error, results, fields) {
    if(error) {
      console.log("mysql error: " + JSON.stringify(error));
      res.sendStatus(500);
      connection.destroy();
      return;
    } else {
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
   
      let sql = "                                           "
              + "SELECT ipv4,                               "
              + "       LCASE(hostname)   AS hn,            "
              + "       UCASE(macaddress) AS mac,           "
              + "       schedulepolicy    AS policy         "
              + "FROM devices                               "
              + "WHERE include                              "
              + "  AND ipv4       IS NOT NULL               "
              + "  AND hostname   IS NOT NULL               "
              + "  AND macaddress IS NOT NULL               ";

      connection.query(sql, [userid], function(error, results, fields) {
        if(error) {
          console.log("mysql error: " + JSON.stringify(error));
          res.sendStatus(500);
          connection.destroy();
          return;
        } else {
          res.json(results);
        }
      });
      connection.end();
    }
  });
});

module.exports = router;
