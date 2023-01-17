
module.exports = {
	method: 'post',
    url: '/api/cron/prdt',
	run: async (req, res, next) => {
        let user = req.user;
        let user_ip = req.ip
        let resultCnt = 0
        let user_id = user.id
        
        //let bet_money = parseInt(req.body.bet_money);
        let prdtList = req.body.items;
        
        // console.log(user_ip)

        for(let i=0; i < prdtList.length; i++){
            let item = prdtList[i]

            let dbPrdthData = await getProduct(item.productId)

            if(dbPrdthData){
                let update_result = await updateProduct(item)
                /*
                console.log(update_result.rows)
                if(update_result.rows.length > 0){
                    resultCnt++
                }
                */
            }else{
                let result = await insertNewProduct(item)
            /*
                if(result.rows.length > 0){
                    resultCnt++
                }
                */
            }
        }

        return res.json({
            status:true,
            resultCnt:resultCnt
        });
    }
}

async function getProduct(prdtCd){
    let resultData = await dbs.getProduct(prdtCd)
    return resultData.data
}

async function insertNewProduct(item) {
    let param = [item.userId, item.prdtId, item.status, item.msg]
    let resultData = await dbs.insertNewProduct(param, function(err, data) {
        return true
    })
};

async function updateProduct(item) {
    let param = [item.productId, 'NIKE', item.type, item.title, item.theme, item.price, item.image, item.href, item.calendar, item.date]
    let resultData = await dbs.updateProduct(param, function(err, data) {
        return true
    })
};
