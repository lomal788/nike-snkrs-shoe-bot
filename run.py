import sys, os
#import telegram
from flask import Flask, jsonify, request
from server import *
from apscheduler.schedulers.background import BackgroundScheduler
import cron
import nike as nk
import threading
import datetime

run_type = 'DRAW'

debug = True

#bot = telegram.Bot(token = '')
#bot.sendMessage(chat_id='',text='test')
sched = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')

app = Flask(__name__)
app.register_blueprint(server)
app.config['JSON_AS_ASCII'] = False

#var_path = os.path.abspath(os.path.dirname(__file__)) + '../var/'
#cron.start_parse(sched)


def run():
    app.run(host='0.0.0.0', port=8000,debug=debug)

if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    #nike = nk.Nike(info=info, proxy=None)
    #browser_thread1 = threading.Thread(target=nike.run)
    #browser_thread1.start()
    #print('cron added')
    #sched.remove_job("shoe_parse")
    #sched.shutdown()
    sched = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')
    cron.start_shoe_parse_job(sched)

if __name__ == '__main__':
    #http Token, Config 파일 체크
    #pip install tendo
    #중복실행 방지 코드
    #from tendo import singleton
    #me = singleton.SingleInstance()
    run()