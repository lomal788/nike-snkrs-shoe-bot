var fs = require('fs');

var express = require('express');
var http = require('http');
var assert = require('assert');
var compression = require('compression');
var path = require('path');
var bodyParser = require('body-parser');
var cookieParser = require('cookie-parser');
var socketIO = require('socket.io');
var ioCookieParser = require('socket.io-cookie');
var _ = require('lodash');
var debug = require('debug')('app:index');
var app = express();

var config = require('../config/config');
var routes = require('./routes');
var database = require('./database');
var lib = require('./lib');

debug('booting webserver');

global.dbs = database

app.set("views", path.join(__dirname, '../views'));

app.locals.recaptchaKey = config.RECAPTCHA_SITE_KEY;
app.locals.buildConfig = config.BUILD;
app.locals.miningFeeBits = config.MINING_FEE/100;

var dotCaching = true;
if (!config.PRODUCTION) {
    app.locals.pretty = true;
    dotCaching = false;
}

app.engine('html', require('ejs').renderFile);

/** Middleware **/
app.use(bodyParser());
app.use(cookieParser());
app.use(compression());


/** App settings **/
app.set('view engine', 'ejs');
app.disable('x-powered-by');
app.enable('trust proxy');


/** Serve Static content **/
var twoWeeksInSeconds = 1209600;
app.use(express.static(path.join(__dirname, '../public'), { maxAge: twoWeeksInSeconds * 1000 }));
app.use('/node_modules', express.static(path.join(__dirname, '../node_modules')), { maxAge: twoWeeksInSeconds * 1000 });

app.use(function(req, res, next) {
    debug('incoming http request');

    var sessionId = req.cookies.id;

    if (!sessionId) {
        res.header('Vary', 'Accept, Accept-Encoding, Cookie');
        res.header('Cache-Control', 'public, max-age=60'); // Cache the logged-out version
        return next();
    }

    res.header('Cache-Control', 'no-cache');

    if (!lib.isUUIDv4(sessionId)) {
        res.clearCookie('id');
        return next();
    }

  database.getUserBySessionId(sessionId, function(err, user) {
    
    if (err) {
            res.clearCookie('id');
            if (err === 'NOT_VALID_SESSION') {
                return res.redirect('/');
            } else {
                console.error('[INTERNAL_ERROR] Unable to get user by session id ' + sessionId + ':', err);
                return res.redirect('/error');
            }
        }
        
        user.error = req.query.err;
        req.user = user;
        next();
    });

});

function errorHandler(err, req, res, next) {

    if (err) {
        if(typeof err === 'string') {
            return res.render('error', { error: err });
        } else {
            if (err.stack) {
                console.error('[INTERNAL_ERROR] ', err.stack);
            } else console.error('[INTERNAL_ERROR', err);

            res.render('error');
        }

    } else {
        console.warning("A 'next()' call was made without arguments, if this an error or a msg to the client?");
    }
}

routes(app);

app.use(errorHandler);

var server = http.createServer(app);

server.listen(config.PORT, function() {
    console.log('Listening on port ', config.PORT);
});

process.on('uncaughtException', function (err) {
    console.error((new Date).toUTCString() + ' uncaughtException:', err.message);
    console.error(err.stack);
    process.exit(1);
});

