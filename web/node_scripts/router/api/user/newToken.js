module.exports = {
	method: 'post',
	url: '/api/user/getNewToken',
	run: async (req, res, next) => {
        let user = req.user;
        let user_ip = req.ip
        let userAgent = req.get('user-agent');
        let resultCnt = 0
        let userId = user.id

        const reulst = updateUserToken(userId, user_ip, userAgent)


	    return res.json({
	        status:true
	    });
	}
}

async function updateUserToken(userId, ipAddress, userAgent){
    let resultData = await dbs.updateUserToken(userId, ipAddress, userAgent)
    return resultData.data
}