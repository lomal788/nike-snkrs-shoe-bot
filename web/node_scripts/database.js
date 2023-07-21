var assert = require('assert');
var uuid = require('uuid');
var config = require('../config/config');

var async = require('async');
var lib = require('./lib');
var pg = require('pg');
var pgTypes = require('pg').types;
var passwordHash = require('password-hash');
var speakeasy = require('speakeasy');
var m = require('multiline');

var databaseUrl = config.DATABASE_URL;

var databaseUrl = 'postgres://'; // DB 접속정보


var config = {
    user: '', // DB 접속정보
    password: '', // DB 접속정보
    server: "127.0.0.1",
    database: 'nikedb',
    stream: true,
    pool: {
            max: 100000,
            min: 0,
            acquireTimeoutMillis: 15000,
            idleTimeoutMillis: 300000,
            idle: 20000,
            evict: 20000,
            acquire: 20000

        },
    debug: {
            packet: true,
            data: true,
            payload: true,
            token: true,
            log: true
        },
    options: {
        tdsVersion: '7_1',
        encrypt: true
    }

}

if (!databaseUrl)
    throw new Error('must set DATABASE_URL environment var');

console.log('DATABASE_URL: ', databaseUrl);

pg = new pg.Pool({
    connectionString: databaseUrl
})

pgTypes.setTypeParser(pgTypes.builtins.INT8, (value) => {
    return parseInt(value);
 });
 
 pgTypes.setTypeParser(pgTypes.builtins.FLOAT8, (value) => {
     return parseFloat(value);
 });
 
 pgTypes.setTypeParser(pgTypes.builtins.NUMERIC, (value) => {
     return parseFloat(value);
 });

function connect(callback) {
    return pg.connect(callback);
}

function query(query, params, callback) {
    if (typeof params == 'function') {
        callback = params;
        params = [];
    }
    else{
      console.log(params);
  }

  doIt();
    function doIt() {
        connect(function(err, client, done) {
            if (err) return callback(err);
            client.query(query, params, function(err, result) {
                done();
                if (err) {
                    if (err.code === '40P01') {
                        console.log('Warning: Retrying deadlocked transaction: ', query, params);
                        return doIt();
                    }
                    return callback(err);
                }

                callback(null, result);
            });
        });
    }
}

exports.query = query;
exports.pg = pg;

pg.on('error', function(err) {
    console.error('POSTGRES EMITTED AN ERROR', err);
});

function getClient(runner, callback) {
    doIt();

    function doIt() {
        connect(function (err, client, done) {
            if (err) return callback(err);

            function rollback(err) {
                client.query('ROLLBACK', done);

                if (err.code === '40P01') {
                    console.log('Warning: Retrying deadlocked transaction..');
                    return doIt();
                }

                callback(err);
            }

            client.query('BEGIN', function (err) {
                if (err)
                    return rollback(err);

                runner(client, function (err, data) {
                    if (err)
                        return rollback(err);

                    client.query('COMMIT', function (err) {
                        if (err)
                            return rollback(err);

                        done();
                        callback(null, data);
                    });
                });
            });
        });
    }
}

exports.changeUserPassword = function(userId, password, callback) {
    assert(userId && password && callback);
    var hashedPassword = passwordHash.generate(password);
    query('UPDATE users SET password = $1 WHERE id = $2', [hashedPassword, userId], function(err, res) {
        if (err) return callback(err);
        assert(res.rowCount === 1);
        callback(null);
    });
};

exports.updateMfa = function(userId, secret, callback) {
    assert(userId);
    query('UPDATE users SET mfa_secret = $1 WHERE id = $2', [secret, userId], callback);
};

exports.validateUser = function(username, password, otp, callback) {
    assert(username && password);

    var hashedPassword = passwordHash.generate(password);


    query('SELECT id, password, mfa_secret FROM users WHERE lower(username) = lower($1)', [username], function (err, data) {
        if (err) return callback(err);

        if (data.rows.length === 0)
            return callback('NO_USER');

        var user = data.rows[0];

        var verified = passwordHash.verify(password, user.password);
        if (!verified)
            return callback('WRONG_PASSWORD');

        if (user.mfa_secret) {
            if (!otp) return callback('INVALID_OTP');

            var expected = speakeasy.totp({ key: user.mfa_secret, encoding: 'base32' });

            if (otp !== expected)
                return callback('INVALID_OTP');
        }

        callback(null, user.id);
    });
};

exports.expireSessionsByUserId = function(userId, callback) {
    assert(userId);

    query('UPDATE sessions SET expired = now() WHERE id = $1 AND expired > now()', [userId], callback);
};


function createSession(client, userId, ipAddress, userAgent, remember, callback) {
    var sessionId = uuid.v4();

    var expired = new Date();
    if (remember)
        expired.setFullYear(expired.getFullYear() + 10);
    else
        expired.setDate(expired.getDate() + 21);

    client.query('INSERT INTO sessions(id, user_id, ip_address, user_agent, expired) VALUES($1, $2, $3, $4, $5) RETURNING id',
        [sessionId, userId, ipAddress, userAgent, expired], function(err, res) {
            if (err) return callback(err);
            assert(res.rows.length === 1);

            var session = res.rows[0];
            assert(session.id);

            callback(null, session.id, expired);
        });
}

exports.getUserBySessionId = function(sessionId, callback) {
    assert(sessionId && callback);
    query('SELECT * FROM users_view WHERE id = (SELECT user_id FROM sessions WHERE id = $1 AND ott = false AND expired > now())', [sessionId], function(err, response) {
        if (err) return callback(err);

        var data = response.rows;
        if (data.length === 0)
            return callback('NOT_VALID_SESSION');

        var user = data[0];

        callback(null, user);
    });
};

exports.createSession = function(userId, ipAddress, userAgent, remember, callback) {

    getClient(function(client, callback) {
        createSession(client, userId, ipAddress, userAgent, remember, callback);
    }, callback);

};

exports.insertNewProduct = async function(param) {
    var sql = "INSERT INTO product"+
    "(PRDT_CD, BRAND, TYPE, TITLE, THEME, PRICE, IMG_URL, PRDT_URL, MSG, RELEASE_DATE)"+
    " values($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) RETURNING id";

    let response = await pg.query(sql,param);
    assert(response.rows.length === 1);
    var data = response.rows[0];
    assert(data.id);

    //console.log(response)
    return {
        err : null,
        data : data.id
    }
};

exports.updateProduct = async function(param) {
    var sql = "UPDATE product set "+
    "PRDT_CD = $1, BRAND = $2, TYPE = $3, TITLE = $4" +
    ", THEME = $5, PRICE = $6, IMG_URL = $7, PRDT_URL = $8" +
    ", MSG = $9, RELEASE_DATE = $10"+
    " where PRDT_CD = '" + param[0] + "'"

    let response = await pg.query(sql,param);

    return {
        err : null,
        data : null
    }
};


exports.getProduct = async function(prdtCd) {
    var sql = "SELECT * FROM product ";
    var option = ''
    option += "WHERE PRDT_CD = '" + prdtCd + "'"
    sql += option

    let response = await pg.query(sql,'');
    var data = response.rows[0];

    return {
        err : null,
        data : data
    }
};

exports.getProductWithCron = async function(prdtId,userId) {
    var sql = "SELECT P.*, PS.id as cronId, PS.size as cronSize FROM product P ";
    var option = ''

    sql += " LEFT JOIN prdt_schedule PS"+
    " ON PS.prdt_id = P.id"+
    " AND PS.user_id = "+userId

    option += " WHERE P.id = '" + prdtId + "'"
    sql += option


    let response = await pg.query(sql,'');
    var data = response.rows[0];

    return {
        err : null,
        data : data
    }
};

exports.getProductList = async function(option) {
    var sql = "SELECT *" +
    " ,to_char(release_date::timestamp with time zone, 'MM'::text) as month "+
    " ,to_char(release_date::timestamp with time zone, 'DD'::text) as day "+
    " FROM product " + option +
    " order by release_date asc ";

    let response = await pg.query(sql,'');
    var data = response.rows;

    return {
        err : null,
        data : data
    }
};

exports.insertNewProductSchedule = async function(param) {
    var sql = "INSERT INTO prdt_schedule"+
    "(user_id, prdt_id, status, msg)"+
    " values($1, $2, $3, $4) RETURNING id";

    let response = await pg.query(sql,param);
    assert(response.rows.length === 1);
    var data = response.rows[0];
    assert(data.id);

    return {
        err : null,
        data : data.id
    }
};

exports.getTodayCronList = async function(option) {
    var sql = "select P.title, P.prdt_url, P.type "+
    ",to_char(P.release_date::timestamp with time zone, 'YYYY-MM-DD HH:mi:ss'::text) as time "+
    " from prdt_schedule PS" +
    " join product P ON P.id = PS.prdt_id " +
    " where " +
    " to_char(P.release_date::timestamp with time zone, 'YYYY-MM-DD'::text) = to_char(NOW(), 'YYYY-MM-DD'::text) "+
    " AND PS.user_id = $1";

    let response = await pg.query(sql,option);
    var data = response.rows;

    return {
        err : null,
        data : data
    }
};

exports.getUserCronList = async function(option) {
    var sql = "select P.* "+
    " ,to_char(release_date::timestamp with time zone, 'MM'::text) as month "+
    " ,to_char(release_date::timestamp with time zone, 'DD'::text) as day "+
    ",to_char(P.release_date::timestamp with time zone, 'YYYY-MM-DD HH:mi:ss'::text) as time "+
    " from prdt_schedule PS" +
    " join product P ON P.id = PS.prdt_id " +
    " where " +
    " PS.user_id = $1 "+
    " order by release_date DESC";

    let response = await pg.query(sql,option);
    var data = response.rows;

    return {
        err : null,
        data : data
    }
};


exports.insertUserCron = async function(param) {
    var sql = "INSERT INTO prdt_schedule"+
    "(user_id, prdt_id, size, status, msg)"+
    " values($1, $2, $3, '', '') RETURNING id";
    console.log(sql)

    let response = await pg.query(sql,param);
    assert(response.rows.length === 1);
    var data = response.rows[0];
    assert(data.id);

    //console.log(response)
    return {
        err : null,
        data : data.id
    }
};

exports.updateUserCron = async function(userId, cronId, param) {
    var sql = "UPDATE prdt_schedule set "+
    " prdt_id = $1, size = $2, status = '', " +
    " msg = ''" +
    " where user_id = " + userId +
    " AND id = "  + cronId

    let response = await pg.query(sql,param);

    return {
        err : null,
        data : null
    }
};


exports.getUserCron = async function(userId, cronId) {
    var sql = "SELECT * FROM prdt_schedule ";
    var option = ''
    option += "WHERE user_id = '" + userId + "'"
    option += "AND id = '" + cronId + "'"
    sql += option

    let response = await pg.query(sql,'');
    var data = response.rows[0];

    return {
        err : null,
        data : data
    }
};

exports.delUserPrdtCron = async function(userId, prdtId, param) {
    console.log(userId,prdtId)
    var sql = "DELETE FROM prdt_schedule "+
    " where user_id = " + userId +
    " AND prdt_id = "  + prdtId
    console.log(sql)

    let response = await pg.query(sql,'');

    return {
        err : null,
        data : null
    }
};


exports.updateUserToken = async function(userId, ipAddress, userAgent) {
    var sessionId = uuid.v4();

    var expired = new Date();
        expired.setDate(expired.getDate() + 365);

    var sql = "UPDATE tokens set "+
    " id = $1, ip_address = $2, user_agent = $3, expired = $4 " +
    " where user_id = " + userId

    let response = await pg.query(sql,[sessionId, ipAddress, userAgent, expired]);

    return {
        err : null,
        data : null
    }
};


exports.getUserTokenbyUserId = async function(userId) {
    var sql = "SELECT * FROM tokens ";
    var option = ''
    option += "WHERE user_id = '" + userId + "'"
    sql += option

    let response = await pg.query(sql,'');
    var data = response.rows[0];

    return {
        err : null,
        data : data
    }
};

exports.getUserTokenbyToken = async function(token) {
    var sql = "SELECT * FROM tokens ";
    var option = ''
    option += "WHERE id = '" + token + "'"
    sql += option

    let response = await pg.query(sql,'');
    var data = response.rows[0];

    return {
        err : null,
        data : data
    }
};
