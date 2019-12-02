var express                 = require('express');
var router                  = express.Router();
var CompensationsController = require('../controllers/CompensationsController');

/* GET home page. */
router.get('/getCompensations', CompensationsController.getSlotsToBeCompensated);

module.exports = router;
