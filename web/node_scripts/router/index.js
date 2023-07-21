const fs = require('fs');

module.exports = async (app) => {
    const apis = await readdir(__dirname + '/api');
    for(let i in apis) {
        const spec = apis[i];
        if(spec.indexOf('.js') == -1) {
            const routers = await readdir(__dirname + '/api/' + spec);
            routers.forEach(r => {
                const router = require((__dirname + '/api/' + spec + '/' + r));
                app[router.method.toLowerCase()](router.url, (req,res,next) => router.run(req,res,next));
            });
        } else {
            const router = require((__dirname + '/api/' + spec));
            app.get(router.url, (req,res,next) => router.run(req,res,next));
        }
    }
}

function readdir(path) {
    return new Promise((resolve, reject) => {
        fs.readdir(path, (err, files) => {
            if(err) return reject(err);
            else return resolve(files);
        })
    });
}