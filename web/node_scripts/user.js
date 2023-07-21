var async = require('async');
var lib = require('./lib');
var database = require('./database');
var _ = require('lodash');

var sessionOptions = {
  maxAge:20000000,
    httpOnly: false,
    secure : 'production'
};

exports.login = function(req, res, next) {
  var user = req.user;
  var username = lib.removeNullsAndTrim(req.body.username);
  var password = lib.removeNullsAndTrim(req.body.password);
  var otp = lib.removeNullsAndTrim(req.body.otp);
  var remember = !!req.body.remember;
  var ipAddress = req.ip;
  var userAgent = req.get('user-agent');

  if (!username || !password)
    return res.json({
      status:false,
      data:null,
      msg:'값을 정확히 입력해주세요.'
  });

  database.validateUser(username, password, otp, function(err, userId) {
    if (err) {
      console.log('[Login] Error for ', username, ' err: ', err);
      if (err === 'NO_USER')
        return res.json({
          status:false,
          data:null,
          msg:'등록된 유저아이디가 없습니다'
      });
      if (err === 'WRONG_PASSWORD')
        return res.json({
          status:false,
          data:null,
          msg:'Invalid password'
      });
        return res.json({
          status:false,
          data:null,
          msg:'Unable to validate user ' + username + ': \n' + err
      });

    }
    database.createSession(userId, ipAddress, userAgent, remember, function(err, sessionId, expires) {
      if (err)
        return res.json({
          status:false,
          data:null,
          msg:'Unable to create session for userid ' + userId +  ':\n' + err
      });

      if(remember)
        sessionOptions.expires = expires;

      res.cookie('id', sessionId, sessionOptions);

      return res.json({
        status:true,
        data:null,
        msg:''
    });

    });
  });
};

exports.logout = function(req, res, next) {
  var sessionId = req.cookies.id;
  var userId = req.user.id;

  database.expireSessionsByUserId(sessionId, function(err) {
      if (err)
          return next(new Error('Unable to logout got error: \n' + err));
      res.redirect('/');
  });
};

exports.index = async function(req, res, next) {

  var user = req.user;
  let token = await dbs.getUserTokenbyUserId(user.id)

  res.render('index', { user : user, token: token.data });
};

exports.upcoming = async function(req, res, next) {

  var user = req.user;
  const option = ' where release_date > (current_date-1)::date ';
  let productList = await dbs.getProductList(option)

  res.render('upcoming', { user : user, products: productList.data });
};

exports.inStock = async function(req, res, next) {

  var user = req.user;
  var userId = user.id;

  const option = [userId];
  let productList = await dbs.getUserCronList(option)

  res.render('instock', { user : user, products: productList.data });
};

exports.product = async function(req, res, next) {

  var user = req.user;
  var prdtId = req.params.prdtId;
  var userId = user.id;

  let product = await dbs.getProductWithCron(prdtId,userId)


  let msgs = product.data.msg

  let pKeys = Object.keys(msgs);
  let msg = ''
  console.log(msgs.length)
  console.log(msgs)

  for(var i=0; i < pKeys.length; i++){

    msg += msgs[pKeys[i]]
  }
  // console.log(msg)
  product.data.msg = msg
  console.log(product)


  res.render('product', { product: product.data });
};

exports.account = function(req, res) {
  var user = req.user;

  if(user.userclass=='admin'){
    var admin = 1 ;

    database.getAdminIndexData(function(err,data) {
      if (err) return res.redirect('/admin-change?m=' + err);
      res.render('admin_new/index', { user: user , admin:admin,data:data });
    });


  }else{
    database.getUserListURC(user.username, function(err,dataC) {
     if (err) return res.render('admin/reffral', { user: user ,warning : err });

     if(user.userclass!='admin'){
      user.aduc = dataC.id;
    }
    res.render('user/account', { user: user });
  });

  }
};
