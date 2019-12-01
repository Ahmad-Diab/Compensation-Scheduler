var express      = require('express');
var path         = require('path');
var cookieParser = require('cookie-parser');
var logger       = require('morgan');
var index        = require('./routes/index');
var app          = express();

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', index);

// 500 internal server error handler
app.use(function(err, req, res, next) {
  if (err.statusCode === 404) return next();
  res.status(500).json({
    // Never leak the stack trace of the err if running in production mode
    err: process.env.NODE_ENV === 'production' ? null : err,
    msg: '500 Internal Server Error',
    data: null
  });
});

// 404 error handler
app.use(function(req, res) {
  res.status(404).json({
    err: null,
    msg: '404 Not Found',
    data: null
  });
});


module.exports = app;
