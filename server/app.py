from flask import jsonify, request
from . import server as api
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import nike_shoes_calendar as nc

#api = Blueprint('account_api', __name__)

@api.route('/', methods=['GET', 'POST'])
def visit():
    if request.method == 'GET':
        res = {
        'responseCode':1000,
        'data':'aaa'
        }
        res = nc.get_drawable_items()
        #req.json.get('data')

        return jsonify(res)
    
    if request.method == 'POST':
        name = request.json['visitor_name']
        # mysql 접속 후 cursor 생성하기
        cur = mysql.connection.cursor()
        # DB 데이터 삽입하기
        cur.execute("INSERT INTO visits (visitor_name) VALUES(%s)", [name])
        # DB에 수정사항 반영하기
        mysql.connection.commit()
        # mysql cursor 종료하기
        cur.close()
        return
