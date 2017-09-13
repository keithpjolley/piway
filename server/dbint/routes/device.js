// routes/devices.js

var express  = require('express');
var path     = require('path');
var bcrypt   = require('bcrypt-nodejs');
var mysql    = require('mysql');

var pidbcnf  = require(path.join(__dirname, '..', 'dbconfig', 'pidbcnf'));
var pirouter = pidbcnf.local.pirouter_ro;

var router  = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.sendStatus(400);
});

router.post('/', function(req, res, next) {

  console.log('post/ : 1 ' + JSON.stringify(req.body));

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
      return;
    } else {

      if(!results.length) {
        console.log("mysql noresults: " + results.length);
        res.sendStatus(401);
        return;
      }

      if(!bcrypt.compareSync(req.body.passwd, results[0].password)) {
        console.log("bcrypt no compare: (" + req.body.passwd + " != " + results[0].password + ")");
        res.sendStatus(401);
        return;
      }

      var userid = results[0].id;
    
      connection.query("SELECT * FROM devices WHERE userid = ?", [userid], function(error, results, fields) {
        if(error) {
          console.log("mysql error: " + JSON.stringify(error));
          res.sendStatus(500);
          return;
        } else {
          res.json(fields);
        }
      });
    }
  });
});

module.exports = router;
