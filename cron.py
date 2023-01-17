import time
#from apscheduler.schedulers.blocking import BlockingScheduler
#from . import nike
import nike_shoes_calendar as nc
import nike as nk
import threading
import datetime
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

#sched = BlockingScheduler()
sched = None
url = ''
url = 'https://www.nike.com/kr/launch/?type=upcoming'
# 매일 12시 30분에 실행
#@sched.scheduled_job('interval', seconds=5, id='test_1')
def job1():
    print(f'job1 : {time.strftime("%H:%M:%S")}')

def shoe_macro_job():
	print('Macro Start')
	#list = nc.get_drawable_items()
	#print(list)
	#print('parse end')
	info = {
		'id':config['user']['id'],
		'pw':config['user']['pw'],
		'url':url,
		'payment_type': config['user']['pament_type'],
		'number':config['user']['number'],
		'birth':config['user']['birth'],
		'type':'FW', #FW 신발, AP 의류
		'size':config['user']['size'], # 신발 : ex) 250, 의류 : L FREE, "M", "W", "Y", "C", "XXS", "XS", "S", "L", "XL"
		'random':False, # 사이즈 맞는거없으면 랜덤 구매 True False
		'draw':True,
		'release_time':True,
		'date':datetime.datetime(2022,2,26,9,59,59),
    }

	nike = nk.Nike(info=info, proxy=None)
	browser_thread1 = threading.Thread(target=nike.run)
	browser_thread1.start()

def shoe_parse_job():
	itemList = nc.get_drawable_items()
	print(str(len(itemList)) + '개의 상품을 불러왔습니다.')

def start_parse(cron):
	sched = cron
	print('cron Job Added')
	sched.add_job(shoe_macro_job, 'cron', hour='9', id="parse_product")
	sched.start()
	#job2()

def start_shoe_parse_job(cron):
	sched = cron
	sched.add_job(shoe_macro_job, 'cron', hour='9', minute='53', id="parse_product")
	#shoe_macro_job()
	sched.add_job(shoe_parse_job, 'cron', hour='9', minute='0', id="shoe_parse")
	#shoe_parse_job()
	sched.start()
	