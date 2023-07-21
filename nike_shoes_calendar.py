import requests, json
from bs4 import BeautifulSoup
from datetime import datetime
from flask import jsonify, request

ROOT_URL = 'https://www.nike.com'

API_URL = 'http://localhost'

#화이트 리스트
shoe_list = ['에어 조던', '에어맥스','오프라인','오버브레이크', '에어 프레스토', '에어 모어','블레이저 로우', '업템포','에어 포스','AJKO', 'sacai', '베이퍼와플' 'SB 덩크', '덩크 로우', '덩크 하이', '에어 트레이너', '르브론', '르브론', 'ACG 에어', 'ACG 마운틴']
#블랙 리스트
shoe_black_list = ['Big Kids', 'Little Kids', 'Toddler', 'Jordan']

def get_request(path='/kr'):
    response = requests.get(ROOT_URL + path, headers={
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/85.0.4183.121 Safari/537.36',
    })
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def post_request(data,path=''):
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    data = json.dumps(data)
    response = requests.post(API_URL + path, headers=headers, data=data)
    #soup = BeautifulSoup(response.text, 'html.parser')
    return response

def get_item_info(item_href):
    soup = get_request(item_href)

    draw_wrapper = soup.find_all('p', class_='draw-info')
    buy_wrapper = soup.find_all('div', class_='available-date-component')
    price_wrapper = soup.find('div', class_='headline-5').text

    price_wrapper = price_wrapper.replace('원','')
    price_wrapper = price_wrapper.replace(',','')
    
    description_wrapper = draw_wrapper if draw_wrapper else buy_wrapper
    
    calendar = [
        paragraph.text for paragraph in description_wrapper
    ]

    return {
    'calendar':calendar,
    'price':price_wrapper
    }


def get_drawable_items():
    soup = get_request(
        '/kr/launch/?type=upcoming&activeDate=date-filter:AFTER')
    #print(soup)

    launch_items = soup.find_all('div', class_='product-card')
    #print(launch_items)
    items = []

    for launch_item in launch_items:
        soldout_button = launch_item.find('a', class_='ncss-btn-primary-dark')
        #print(soldout_button)

        if (soldout_button and soldout_button.text.strip() == 'THE DRAW 진행예정'):
        #if (soldout_button and soldout_button.text.strip() == 'Coming Soon'):
            launch_item_information = launch_item.find(
                'a', class_='comingsoon')
            launch_item_image = launch_item.find('img', class_='img-component')
            launch_month = launch_item_information.find('p', class_='headline-4')
            launch_day = launch_item_information.find('p', class_='headline-1')


            shoe_status = [s for s in shoe_list if s in launch_item_information.attrs['title']]
            shoe_status2 = [s for s in shoe_black_list if s in launch_item_information.attrs['title']]

            if len(shoe_status) == 0 or len(shoe_status2) > 0: continue

            nowDate = datetime.now()
            date_time_str = launch_month.text+launch_day.text
            date_time = nowDate.strptime(date_time_str, '%m월%d')

            release_date = datetime(nowDate.year,date_time.month, date_time.day,9,59,59).strftime("%Y/%m/%d, %H:%M:%S")

            item_info = get_item_info(launch_item_information.attrs['href'])
            
            item = {
                'type': 'draw',
                'productId':launch_item_information.attrs['data-tag-pw-rank-product-id'],
                'title': launch_item_information.attrs['title'],
                'theme': launch_item_image.attrs['alt'],
                'image': launch_item_image.attrs['data-src'],
                'href': launch_item_information.attrs['href'],
                'date' : release_date,
                'price' : item_info['price'],
                'calendar' : item_info['calendar'],
            }
            items.append(item)
            #print(item)

        if (soldout_button and soldout_button.text.strip() == 'Coming Soon'):
            launch_item_information = launch_item.find(
                'a', class_='comingsoon')
            launch_item_image = launch_item.find('img', class_='img-component')
            launch_month = launch_item_information.find('p', class_='headline-4')
            launch_day = launch_item_information.find('p', class_='headline-1')

            shoe_status = [s for s in shoe_list if s in launch_item_information.attrs['title']]
            shoe_status2 = [s for s in shoe_black_list if s in launch_item_information.attrs['title']]

            if len(shoe_status) == 0 or len(shoe_status2) > 0: continue

            nowDate = datetime.now()
            date_time_str = launch_month.text+launch_day.text
            date_time = nowDate.strptime(date_time_str, '%m월%d')

            release_date = datetime(nowDate.year,date_time.month, date_time.day,9,59,59).strftime("%Y/%m/%d, %H:%M:%S")
            #release_date = release_date.strftime("%Y/%m/%d, %H:%M:%S")

            item_info = get_item_info(launch_item_information.attrs['href'])
            item = {
                'type': 'soon',
                'productId':launch_item_information.attrs['data-tag-pw-rank-product-id'],
                'title': launch_item_information.attrs['title'],
                'theme': launch_item_image.attrs['alt'],
                'image': launch_item_image.attrs['data-src'],
                'href': launch_item_information.attrs['href'],
                'date' : release_date,
                'price' : item_info['price'],
                'calendar' : item_info['calendar'],
                }

            items.append(item)
            #print(item)

            #현재 살수있는거 Buy
        if (soldout_button and soldout_button.text.strip() == 'Buy'):
            launch_item_information = launch_item.find(
                'a', class_='card-link')
            launch_item_image = launch_item.find('img', class_='img-component')
            launch_month = launch_item_information.find('p', class_='headline-4')
            launch_day = launch_item_information.find('p', class_='headline-1')

            shoe_status = [s for s in shoe_list if s in launch_item_information.attrs['title']]
            shoe_status2 = [s for s in shoe_black_list if s in launch_item_information.attrs['title']]

            if len(shoe_status) == 0 or len(shoe_status2) > 0: continue

            nowDate = datetime.now()
            date_time_str = launch_month.text+launch_day.text
            date_time = nowDate.strptime(date_time_str, '%m월%d')

            release_date = datetime(nowDate.year,date_time.month, date_time.day,9,59,59).strftime("%Y/%m/%d, %H:%M:%S")
            #release_date = release_date.strftime("%Y/%m/%d, %H:%M:%S")
            item_info = get_item_info(launch_item_information.attrs['href'])
            item = {
                'type': 'Buy',
                'productId':launch_item_information.attrs['data-tag-pw-rank-product-id'],
                'title': launch_item_information.attrs['title'],
                'theme': launch_item_image.attrs['alt'],
                'image': launch_item_image.attrs['data-src'],
                'href': launch_item_information.attrs['href'],
                'date' : release_date,
                'price' : item_info['price'],
                'calendar' : item_info['calendar'],
                }
            items.append(item)
            #print(item)
    param = {
    'items' : items
    }
    responsetest = post_request(param,'/api/prdt/product')
    print(responsetest)
    return items


if __name__ == "__main__":

    list = get_drawable_items()
    #print(list)

