
module.exports = {
	method: 'post',
	url: '/api/user/delProduct',
	run: async (req, res, next) => {
        let user = req.user;
        let user_ip = req.ip
        let resultCnt = 0
        let user_id = user.id
        
        //let bet_money = parseInt(req.body.bet_money);
        let prdtId = req.body.prdtId;

        await delUserPrdtCron(user_id, prdtId)

        return res.json({
            status:true,
            resultCnt:resultCnt
        });
    }
}

async function delUserPrdtCron(userId, prdtId) {
    let param = [userId, prdtId]
    let resultData = await dbs.delUserPrdtCron(userId, prdtId, param)
    return resultData.data
};