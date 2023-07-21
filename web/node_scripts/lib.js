var assert = require('better-assert');

exports.isUUIDv4 = function(uuid) {
    return (typeof uuid === 'string') && uuid.match(/^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i);
};

exports.removeNullsAndTrim = function(str) {
    if(typeof str === 'string')
        return str.replace(/\0/g, '').trim();
    else
        return str;
};