
module.exports = {
    method: 'get',
    url: '/api/cron/today-cron',
    run: async (req, res, next) => {
        let user_ip = req.ip
        let resultCnt = 0

        let token = req.headers.token
        const tokenStatus = await isUUIDv4(token)


        if (!tokenStatus)
            return res.json({
                status:false,
                msg:'잘못된 토근입니다.',
            });



        let tokenInfo = await getUserTokenbyToken(token)

        if( tokenInfo === null)
            return res.json({
                status:false,
                msg:'잘못된 토근입니다.',
            });

        let userId = tokenInfo.user_id

        let result = await getTodayCronList(userId)

        return res.json({
            status:true,
            data:result,
        });
    }
}

async function isUUIDv4 (uuid) {
    return (typeof uuid === 'string') && uuid.match(/^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i);
};

async function getTodayCronList(userId){
    let resultData = await dbs.getTodayCronList([userId])
    return resultData.data
}

async function getUserTokenbyToken(token){
    let resultData = await dbs.getUserTokenbyToken(token)
    return resultData.data
}
