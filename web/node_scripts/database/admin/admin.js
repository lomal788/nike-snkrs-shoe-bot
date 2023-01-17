var database = require('..../database');

exports.InsertTotoBet2 = async function(user_id,type,bet_id,home_dis,draw_dis,away_dis,bet_dis,bet_part) {
    var sql = "INSERT INTO match_bet(user_id,type,bet_id,home_dis,draw_dis,away_dis,bet_dis,bet_part)"+
    " values($1,$2,$3,$4,$5,$6,$7,$8) RETURNING id";

    let response = await pg.query(sql,[user_id,type,bet_id,home_dis,draw_dis,away_dis,bet_dis,bet_part]);
    assert(response.rows.length === 1);
    var data = response.rows[0];
    assert(data.id);

    //console.log(response)
    return {
        err : null,
        data : data.id
    }
};