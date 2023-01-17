
//Library
var assert = require('better-assert');
var lib = require('./lib');
var database = require('./database');
var numeral = require('numeral');

//etc
var router = require('./router');
var user = require('./user');

function staticPageLogged(page, loggedGoTo) {
	return function(req, res) {
		var user = req.user;
		if (!user){ 
			return res.render(page);
		}
		if (loggedGoTo) return res.redirect(loggedGoTo);
		res.render(page, {
			user: user
		});
	}
}

function restrict(req, res, next) {
	if (!req.user) {
		res.status(401);
		if (req.header('Accept') === 'text/plain')
			res.send('Not authorized');
		else
			res.render('401');
		return;
	} else
	next();
}

function restrictRedirectToHome(req, res, next) {
	if(!req.user) {
		res.redirect('/login');
		return;
	}
	next();
}

module.exports = async function(app) {
	await router(app);

	app.get('/login', staticPageLogged('login'));
	app.get('/logout', restrictRedirectToHome, user.logout);

	app.get('/', restrictRedirectToHome, user.index);
	app.get('/instock', restrictRedirectToHome, user.inStock);
	app.get('/upcoming', restrictRedirectToHome, user.upcoming);

	app.get('/product/:prdtId', restrictRedirectToHome, user.product);
	app.post('/login', user.login);

	app.get('/error', function(req, res, next) { 
		return res.render('error');
	});

	app.get('*', function(req, res) {
		res.status(404);
		res.render('404');
	});
};
