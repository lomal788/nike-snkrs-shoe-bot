from flask import jsonify, request
from . import server as api

#api = Blueprint('account_api', __name__)

@api.route('/healthcheck', methods=['GET', 'POST'])
def healthcheck():
    if request.method == 'GET':
        res = {
        'responseCode':200,
        'data':True
        }
        #req.json.get('data')

        return jsonify(res)
