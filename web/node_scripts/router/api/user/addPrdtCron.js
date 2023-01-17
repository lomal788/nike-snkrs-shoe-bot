
module.exports = {
	method: 'post',
    url: '/api/user/product-cron',
	run: async (req, res, next) => {
        let user = req.user;
        let user_ip = req.ip
        let resultCnt = 0
        let userId = user.id
        
        // let userId = 1;
        let cronId = parseInt(req.body.cronId);
        let prdtId = parseInt(req.body.prdtId);
        let size = req.body.size;

        let cronData = null;

        if(cronId) cronData = await getUserCron(userId, cronId)

        if(cronData){
            let update_result = await updateUserCron(userId, cronId, prdtId, size)
        }else{
            let result = await insertUserCron(userId, prdtId, size)
        }

        return res.json({
            status:true,
            resultCnt:resultCnt
        });
    }
}

async function getUserCron(userId, cronId){
    let resultData = await dbs.getUserCron(userId, cronId)
    return resultData.data
}

async function insertUserCron(userId, prdtId, size) {
    let param = [userId, prdtId, size]
    let resultData = await dbs.insertUserCron(param)
    return resultData.data
};

async function updateUserCron(userId, cronId, prdtId, size) {
    let param = [prdtId, size]
    let resultData = await dbs.updateUserCron(userId, cronId, param)
    return resultData.data
};
