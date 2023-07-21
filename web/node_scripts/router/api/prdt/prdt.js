module.exports = {
    method: 'get',
    url: '/api/prdt/product',
    run: async (req, res, next) => {
        let user_ip = req.ip
        let resultCnt = 0

        let option = ""

        let result = await getProductList(option)

        return res.json({
            status:true,
            data:result,
        });
    }
}

async function getProductList(option){
    let resultData = await dbs.getProductList(option)
    return resultData.data
}
