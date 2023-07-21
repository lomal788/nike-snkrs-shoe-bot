from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
import time
import multiprocessing
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import *
import six
import pause
import datetime
import threading
import re
import signal, os
import sys
import requests, json
import telegram
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

bot = telegram.Bot(token='TelegramBot토큰')
chat_id = config['system']['telegram_chat_id']

options = webdriver.ChromeOptions()
#options.add_argument('headless')
#options.add_argument("no-sandbox")
#options.add_argument('window-size=1920x1080')
#options.add_argument("disable-gpu")
#options.add_argument("lang=ko_KR")
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

clothesSize = ['90(S)','95(S)','95(M)','100(M)','100(L)','105(L)','105(XL)','110(XL)','115(2XL)']

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    }

options.add_argument("--log-level=3")  # 콘솔로그 제거
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36')
options.add_argument("--disable-popup-blocking");

screenshot_path = 'D:/Programing/nike/img/'

class Nike:

    def __init__(self,info,url='',proxy=None):
        self.info=info
        self.proxy = proxy
        self.url = info['url']
        self.url = 'https://www.nike.com/kr/launch/?type=upcoming'

        
        responseaa = self.get_request('/api/cron/today-cron')
        print(responseaa)

        if responseaa['status'] is False:
            print('잘못된 토큰입니다.')
            self.driver.quit()


        self.pList = responseaa['data']

    def get_request(self, path='/kr',data=''):
        response = requests.get('http://localhost' + path, headers={
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/85.0.4183.121 Safari/537.36',
            'token' : config['system']['token']
        })
        json_val = json.loads(response.text)
        return json_val

    def run(self):

        if self.proxy:
            options.add_argument("--proxy-server="+self.proxy);

        self.driver = webdriver.Chrome(executable_path=r"D:/Programing/nike/chromedriver.exe",options=options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                    """
        })

        self.driver.maximize_window()
        self.driver.set_page_load_timeout(10)

        self.driver.get(self.url)
        self.driver.implicitly_wait(10)


        self.closePopup()

        #self.pList = [{'prdt_url':'','type':'','time':'2022-06-12 09:59:59'}]
        
        for i in range(len(self.pList)):
            item = self.pList[i]
            nowDate = datetime.datetime.now()
            

            self.url = 'https://www.nike.com' + item['prdt_url']
            
            self.info['draw'] = item['type']
            self.info['date'] = nowDate.strptime(item['time'], '%Y-%m-%d %H:%M:%S')

            #self.url = 'https://www.nike.com/kr/launch/t/men/fw/basketball/555088-702/IkC2r3/air-jordan-1-retro-high-og'
            #self.info['draw'] = 'Buy'
            #self.info['date'] = nowDate.strptime(item['time'], '%Y-%m-%d %H:%M:%S')


            msg = 'url : ' + self.url
            msg += '\ntype : ' +self.info['draw']
            msg += '\n상태 : 시작'


            bot.sendMessage(chat_id=chat_id, text=msg)
            skip_retry_login = True

            try:
                self.login()
            except TimeoutException as e:
                skip_retry_login = True
                six.reraise(Exception, e, sys.exc_info()[2])
            except Exception as e:
                print("Failed to login: " + str(e))
                six.reraise(Exception, e, sys.exc_info()[2])

            if skip_retry_login is False:
                try:
                    retry_login(driver=driver, username=username, password=password)
                except Exception as e:
                    print("Failed to retry login: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])
            bot.sendMessage(chat_id=chat_id, text='로그인 성공')
            if self.info['release_time']:
                #LOGGER.info("Waiting until release time: " + release_time)
                bot.sendMessage(chat_id=chat_id, text='시간 대기')
                pause.until(self.info['date'])

            if self.info['draw'] == 'draw':
                print('draw')
                self.drawProcess()
            else:
                print('buy')
                self.buyingProcess()
            self.driver.quit()
            #
        
        self.driver.quit()


    def drawProcess(self):
        # //*[@id="checkTerms"]/label
        #//*[@id="optionPrivacy"]/label
        #//*[@id="selectSize"]
        #드로우 버튼
        #//*[@id="btn-login"]
        #드로우 결과확인
        #//*[@id="btn-drawiswin"]
        #/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div[3]
        
        skip_add_address = False
        skip_select_shipping = False
        skip_payment = False
        num_retries_attempted = 0
        num_retries = 5
        is_failed = False

        while True:
            try:
                try:
                    print("2.Draw Requesting page: ")
                    self.driver.get(self.url)
                except TimeoutException:
                    print("Page load timed out but continuing anyway")


                wait_until_visible(driver=self.driver, xpath='/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div[2]/div/div/div/form/div/div[2]/a', duration=5)
                term_label_xpath = '//*[@id="checkTerms"]/label/i'
                
                #wait_until_clickable(self.driver, xpath=term_label_xpath, duration=10)
                self.driver.find_element_by_xpath(term_label_xpath).click()

                sms_label_xpath = '//*[@id="optionPrivacy"]/label/i'

                #wait_until_clickable(self.driver, xpath=sms_label_xpath, duration=10)
                self.driver.find_element_by_xpath(sms_label_xpath).click()
                
                try:
                    self.findSizeInput()
                except Exception as e:
                    nowDate = datetime.datetime.now()
                    self.driver.save_screenshot(screenshot_path+'FindSizeErr_'+nowDate.strftime("%Y-%m-%d %H-%M")+'.png')
                    with open(screenshot_path+"FindSizeErr_"+nowDate.strftime("%Y-%m-%d %H-%M")+'.txt', "w", encoding='UTF-8') as f:
                        f.write(self.driver.page_source)
                    print(str(e))
                    continue

                try:
                    self.click_draw_button()
                except Exception as e:
                    nowDate = datetime.datetime.now()
                    self.driver.save_screenshot(screenshot_path+'clickBuyButtonErr_'+nowDate.strftime("%Y-%m-%d %H-%M")+'.png')
                    with open(screenshot_path+"clickBuyButtonErr_"+nowDate.strftime("%Y-%m-%d %H-%M")+'.txt', "w", encoding='UTF-8') as f:
                        f.write(self.driver.page_source)
                    print(str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])

                bot.sendMessage(chat_id=chat_id, text='드로우 성공')
                break
            except Exception as e:
                if num_retries and num_retries_attempted < num_retries:
                    num_retries_attempted += 1
                    skip_add_address = False
                    skip_select_shipping = False
                    skip_payment = False
                    continue
                else:
                    bot.sendMessage(chat_id=chat_id, text='드로우 실패')
                    print("draw failed")
                    print(str(e))
                    nowDate = datetime.datetime.now()
                    self.driver.save_screenshot(screenshot_path+"draw_failed"+nowDate.strftime("%Y-%m-%d %H-%M")+'.png')
                    with open(screenshot_path+"draw_failed"+nowDate.strftime("%Y-%m-%d %H-%M")+'.txt', "w", encoding='UTF-8') as f:
                        f.write(self.driver.page_source)
                    is_failed = True
                    break

        if is_failed:
            print('failed')
            #self.driver.quit()
        else:
            html_path = True
            if screenshot_path:
                #LOGGER.info("Saving screenshot")
                nowDate = datetime.datetime.now()
                self.driver.save_screenshot(screenshot_path+"드로우 성공"+nowDate.strftime("%Y-%m-%d %H-%M")+'.png')

            if html_path:
                print("Saving HTML source")
                nowDate = datetime.datetime.now()
                with open(screenshot_path+"드로우 성공"+nowDate.strftime("%Y-%m-%d %H-%M")+'.txt', "w", encoding='UTF-8') as f:
                    f.write(self.driver.page_source)
            #self.driver.quit()

        #draw-date
        #/html/body/div[1]/div/div[1]/div[2]/dl
        #남은시간 텍스트
        #/html/body/div[1]/div/div[1]/div[2]/dl/dt
        #실제로 Draw 남은시간 00:00:00
        #/html/body/div[1]/div/div[1]/div[2]/dl/dd



        #드로우 완료텍스트 진행중일때 해당 버튼 텍스트
        #/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div[2]
        #드로우 진행중 텍스트
        # -THE DRAW 진행예정
        #/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div[2]/div

        #드로우 완료 텍스트
        #/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div[2]/div/span

    def closePopup(self):
        try:
            popupElement = self.driver.find_element_by_xpath('//*[@id="update-profile"]')

            if popupElement:
                close_button = self.driver.find_element_by_xpath('//*[@id="update-profile"]/div/a')
                close_button.click()
        except Exception as e:
            print(e)
        
    def click_draw_button(self):
        #xpath = '//*[@id="btn-drawiswin"]'
        xpath = '//*[@id="btn-buy"]'
        #xpath = '//*[@id="btn-login"]'
        

        #LOGGER.info("Waiting for buy button to become present")
        element = wait_until_present(self.driver, xpath=xpath, duration=10) 
        
        #LOGGER.info("Clicking buy button")
        self.driver.execute_script("arguments[0].click();", element)


    def buyingProcess(self):

        skip_add_address = False
        skip_select_shipping = False
        skip_payment = False
        num_retries_attempted = 0
        num_retries = 5
        is_failed = False

        while True:
            try:

                try:
                    print("2.buy Requesting page: ")
                    self.driver.get(self.url)
                except TimeoutException:
                    print("Page load timed out but continuing anyway")

                try:
                    self.findSizeInput()
                except Exception as e:
                    print(str(e))
                    continue

                try:
                    self.click_buy_button()
                except Exception as e:
                    print("Failed to click buy button: "+str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])

                self.order()
                #print('구매완')
                self.payment()
                # self.payment()
                if screenshot_path:
                    #LOGGER.info("Saving screenshot")
                    nowDate = datetime.datetime.now()
                    self.driver.save_screenshot(screenshot_path+'buy_success'+nowDate.strftime("%Y-%m-%d %H-%M")+'.png')
                    with open(screenshot_path+"buy_success"+nowDate.strftime("%Y-%m-%d %H-%M")+'.txt', "w", encoding='UTF-8') as f:
                        f.write(self.driver.page_source)
                print('구매완료')
                bot.sendMessage(chat_id=chat_id, text='구매 성공')
                break
            except Exception:
                if num_retries and num_retries_attempted < num_retries:
                    num_retries_attempted += 1
                    skip_add_address = False
                    skip_select_shipping = False
                    skip_payment = False
                    continue
                else:
                    bot.sendMessage(chat_id=chat_id, text='구매 실패')
                    print("buy failed")
                    nowDate = datetime.datetime.now()
                    self.driver.save_screenshot(screenshot_path+"buy_failed"+nowDate.strftime("%Y-%m-%d %H-%M")+'.png')
                    with open(screenshot_path+"buy_failed"+nowDate.strftime("%Y-%m-%d %H-%M")+'.txt', "w", encoding='UTF-8') as f:
                        f.write(self.driver.page_source)
                    is_failed = True
                    break
        #self.driver.quit()

    def login(self):
        # 쿠키 담기
        #cookies = ""
        #cookies = {"NikeCookie":"ok","geoloc":"cc=KR,rc=,tp=vhigh,tz=GMT+9,la=37.57,lo=127.00","bm_sz":"B65E3CF0BD0876488766C8FA6B83286F~YAAQR5c7F2ZCwFl8AQAAjNGh2w1+gh0/Hg5IRDpDVJPBzlesUpsnLxS98VARSJ9Bbl6vmoJNNHo45nLVP2pGbCHO5Ruv3ZgaYAPKlOstqDYfYhYT5Hig53FDmdMkCeL5Z4r1rN4NT3FQfA/rbhDybV8HHhDnqOmBl+9P3c1jC5hkGUtWdH6TsWI+Bq2D7wVcvr334A5mBGKM+Z7oavEsTI+VYx+uDSY3ubBAxtf1TgaoPS3RVRsKdKJjksj/wW83J3Pb0EZiEkofNcn8xOtlHwWrPdIFZnGtNBXTRpxvArhvWQ1Uas4le3BpXy2wP3aP9BVZqYZFX+m/8WfTBsNIVSMek+csejiV9VCl70HnwCP6CdUJObWUP1q6iMccibJUUI0iL93Izy3yzkCd1THB~3355956~3420469","WHATAP":"zm4ik3l2shmjs","nike1_CID":"3a33070196e5461288b4ea982d09ff3b","USERID":"5210656944","_gcl_au":"1.1.676621721.1635772376","s_ips":"1034","s_tp":"4707","v15":"1635772376338","_ga":"GA1.2.2049382479.1635772376","_gid":"GA1.2.1099210821.1635772376","c5":"nikestorekr%3Esnkrs%3Elaunch%3Eupcoming","c6":"grid%20wall","AWSALBTG":"j38lbmkYpZHleVpvbXM2aEflgyr7rUvPj8wQkd+c50r7LUrHZPysAVf1p6GEElF+d5ez+nRgGwDnmj9kI9mV2XIoNf9Mn8gBh9tGEI0xiyxX77uZBvCDYkJu2NVVI/1zOMv1SvnbKIvFyFuGZDuJcnigLsU5DMw3HJU8HccgBpU/","AWSALB":"S2pKmQjcuHP/ENqJyjR9+DN+l+Yt8e4NJ9KcIFiQ81Pg2gJAOZ3GcJH7Bo2AXDGTpI0a/V627fXczyzi7x473+dArhsfol/tSkSjLdQafKCtI5B12pyWimV2SmtY","s_ecid":"MCMID%7C85063252127463031341962242763490567931","AMCVS_F0935E09512D2C270A490D4D%40AdobeOrg":"1","wcs_bt":"s_150ba4df84f2:1635772377","s_ppv":"undefined%2C22%2C22%2C1034%2C1%2C4","s_cc":"true","cto_bundle":"C4mRD19MdmxaVU9EUlpFb1FodWxKcGRaZlh2N09lTWNPSEdmVXA3JTJCMVJWTEp4b1JUQlRMM1BaTjVFM1JjUnI0b0ZNelo5TFQwbHNvS0Rld3B1JTJCNEdDQzcyeWFnTGtxJTJGdk1tcHJoeGFSc2VoaVdTMmJacmczalQyeWdvWVA2Y1NZWUdHTA","AMCV_F0935E09512D2C270A490D4D%40AdobeOrg":"-1124106680%7CMCIDTS%7C18933%7CvVersion%7C5.2.0%7CMCMID%7C85063252127463031341962242763490567931%7CMCAID%7CNONE%7CMCOPTOUT-1635779577s%7CNONE%7CMCAAMLH-1636377177%7C11%7CMCAAMB-1636377177%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCCIDH%7C-218816571%7CMCSYNCSOP%7C411-18940","RT":"\"z=1&dm=nike.com&si=ec6396c2-2ebb-4933-b44b-9904faadd485&ss=kvgog3af&sl=5&tt=5y3&bcn=%2F%2F684d0d36.akstat.io%2F&obo=2&ld=6xv3\"","s_ptc":"0.03%5E%5E0.00%5E%5E0.00%5E%5E0.00%5E%5E0.89%5E%5E0.00%5E%5E1.75%5E%5E0.01%5E%5E2.78","_abck":"26EE418139438D70D25C97A120E8551C~-1~YAAQR5c7F0hDwFl8AQAAkOOh2wZuxdzyxyd9Irb/NTyN+jVz6csO8P9LfvFoNBabb3qurlHyWPt+71pfl2HAsuvzr+JRQg9iNb/bzO3LJSxH+Bv0ciNm/crZBqYdAyPMTRboDgNiILtkpl35yn2/XhTlBgYJi6/YDoaxOZAmD81jMX68vPADS7GZ4emsipAQ8unH/0A/cfSDCq1cGLmMB7C9v1MKMDGSCBDLeEr6/37ZTtZjuY5g5AnhYbIu8UegyiySJRiO+otTYMCv6dUpd4RwCPk6hTD1DyCqxe+lfEcZmbuajk+IGRGTkHMHUpH7G/wbtgyvb6C6oAs+zxbvHpDWkiXFfVufH5FIsqc+2K5lbFLnX1iDee4KhO4JozR8P73qmRo3r3XQS6XH7qUE+x8KPO/FFqgYmPvIh+GXbFyRnXrhvIzP1Gwq8Bjua/XTeY1D83E1n8IE3/QjBRAJeZxxikwijVg7SZbXkiCZ4+29bLy1+Jxqlj3/VT3LGimJ8w==~-1~||-1||~-1","anonymousId":"DSWX310B73727F63D5F1FE0605853AF94FB0","ppd":"upcoming|snkrs>upcoming"}
        #for cookie in cookies:
            #driver.add_cookie(cookie)

        try:
            print("1.Requesting page")
            self.driver.get('https://www.nike.com/kr/launch/logout')
            self.driver.get('https://www.nike.com/kr/launch/?type=upcoming')
            self.closePopup()
        except TimeoutException:
            print("Page load timed out but continuing anyway")
        print("Waiting for login fields to become visible")


        wait_until_visible(driver=self.driver, xpath='//*[@id="jq_m_right_click"]/div/ul/li[2]/a', duration=5)
        print("Click Login Button")

        loginbutton = self.driver.find_element_by_xpath('//*[@id="jq_m_right_click"]/div/ul/li[2]/a')
        loginbutton.click()

        print("Entering username and password")
        wait_until_visible(driver=self.driver, xpath='//*[@id="common-modal"]/div/div/div', duration=2)
        email_input = self.driver.find_element_by_xpath('//*[@id="j_username"]')
        email_input.clear()
        email_input.send_keys(self.info['id'])

        password_input = self.driver.find_element_by_xpath('//*[@id="j_password"]')
        password_input.clear()
        password_input.send_keys(self.info['pw'])

        login = self.driver.find_element_by_xpath('//*[@id="common-modal"]/div/div/div/div/div[2]/div/div[2]/div/button') #로그인버튼을 찾아줌
        login.click() #로그인 버튼을 눌러줌

        wait_until_visible(driver=self.driver, xpath='//*[@id="jq_m_right_click"]/div/ul/li[1]/div/div/label/span', duration=5)
        print("Successfully logged in")


    def retry_login():
        num_retries_attempted = 0
        num_retries = 5



    def findSizeInput(self):

        self.driver.implicitly_wait(1)
        #wait_until_visible(self.driver, class_name="select-box", duration=2)
        # 사이즈 찾기
        #driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div/div/div/div/form/div/div[1]/ul/li[5]').click()
        #driver.execute_script("location.reload()")

        while True:
            #/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div/div
            CmSoonBtn = self.driver.find_elements_by_class_name('btn-coming-soon')

            try:
                if CmSoonBtn:
                    print('안열림 새로고침')
                    self.driver.get(self.url)
                else:
                    print('열림 구매프로세스 시작')
                    break
            except NoSuchElementException:
                self.driver.get(self.url)


        wait_until_visible(self.driver, xpath='/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div/div/div/div/form/div/div[1]', duration=10)
        size_list = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div/div/div/div/form/div/div[1]").text

        if re.search("[a-zA-Z]", size_list):
            #옷 인경우

            size=Select(self.driver.find_element_by_xpath('//*[@id="selectSize"]'))
            matching = [item.text for item in size.options if self.info['size'] in item.text]

            if matching:
                size.select_by_visible_text(matching[0])
            else:
                size.select_by_visible_text('80(M)')

        else:
            #신발인경우
            print(size_list)
            #is_enabled()
            # driver.find_element_by_xpath("//li[@data-qa='size-available']/button").text
            size=Select(self.driver.find_element_by_xpath('//*[@id="selectSize"]'))

            #for index in range(len(size.options)):
                #print(size.options[index])
                #select = Select(driver.find_element_by_name('kategorija'))
                #size.select_by_visible_text(self.info['size']) # select visible text
                #select.select_by_index(index)

            

            print(size)
            #for item in size:
                #print(item)

            size.select_by_visible_text(self.info['size']) # select visible text


    def click_buy_button(self):
        xpath = '//*[@id="btn-buy"]'

        element = wait_until_present(self.driver, xpath=xpath, duration=10)         
        print("Clicking buy button")
        self.driver.execute_script("arguments[0].click();", element)

    def order(self):
        print('결재 페이지 진입')
        while True:

            try:
                btn1 = self.driver.find_element_by_xpath('// *[ @ id = "btn-next"]')
                btn1.click()
                break
            except NoSuchElementException:
                try :
                    popup = self.driver.find_element_by_xpath('/html/body/div[17]/div')
                    if popup:
                        text = self.driver.find_element_by_xpath("/html/body/div[17]/div/div/div[1]").text
                        print(text)
                        self.driver.find_element_by_xpath('/html/body/div[17]/div/div/div[2]/button').click()
                except NoSuchElementException:
                    continue
                print("No Found")


        #paymentReviewXpath = '// *[ @ id = "payment-review"] / div[1] / ul / li[1] / div / div[1] / h6'
        #paymentReview = wait_until_present(self.driver, xpath=paymentReviewXpath, duration=10)
        #paymentReview.click()

        #paymentReviewXpath2 = '//*[@id="payment-review"]/div[1]/ul/li[2]/form/div/span/label/span'
        #paymentReview2 = wait_until_present(self.driver, xpath=paymentReviewXpath2, duration=10)
        #paymentReview2.click()

        self.driver.implicitly_wait(1)
        self.driver.find_element_by_xpath('// *[ @ id = "payment-review"] / div[1] / ul / li[1] / div / div[1] / h6').click()
        self.driver.implicitly_wait(1)
        self.driver.find_element_by_xpath('//*[@id="payment-review"]/div[1]/ul/li[2]/form/div/span/label/span').click()
        self.driver.implicitly_wait(2)

        return

        isSuccess = False
        while True:
            print(isSuccess)
            if isSuccess:
                break
            time.sleep(0.1)
            try:
                self.driver.implicitly_wait(1)
                checkoutBtn = self.driver.find_element_by_xpath('//*[@id="complete_checkout"]')

                #Access Denined 에러
                #/html/body/div[17]/div[1]
                
                if checkoutBtn:
                    checkoutBtn.click()
                iframe = self.driver.find_element_by_xpath("/html/body/div[17]/iframe[2]")
                if iframe:
                    isSuccess = True
                else:
                    try:
                        alertBtn = self.driver.find_element_by_xpath('/html/body/div[17]/div/div/div[2]/button')
                        if alert:
                            alertBtn.click()
                            continue
                    except NoSuchElementException:
                        try:
                            iframe = self.driver.find_element_by_xpath("/html/body/div[17]/iframe[2]")
                            if iframe:
                                isSuccess = True
                        except NoSuchElementException:
                            continue
            except NoSuchElementException:
                #ElementClickInterceptedException:
                continue
            except KeyboardInterrupt:
                sys.exit()
            except:
                continue


        print('구매버튼 클릭 성공')

            #팝업 DIV
            #/html/body/div[18]
            #팝업 확인버튼
            #/html/body/div[18]/div/div/div[2]/button
            #팝업 내용
            #[결제포기] 사용자가 결제를 취소하셨습니다
            #/html/body/div[18]/div/div/div[1]


            #신한카드

            #전체동의
            #/html/body/div[17]/iframe[1]
            #//*[@id="iframe"]
            #신한카드
            #//*[@id="cardCode22"]
            #앱카드 버튼
            #//*[@id="testLoad"]/div[2]/div[2]/div[4]/ul[1]/li/label/span
            #//*[@id="shinhanApp"]

            #다음버튼
            #//*[@id="CardBtn"]

            #결재페이지 생성
            #/html/body/div/form/div[1]/div[2]/div[2]/div
            #/html/body
            #결재코드 번호
            #/html/body/div/form/div[1]/div[2]/div[2]/div/div[2]/span[1]
            #QR코드
            #/html/body/img

            #결재 완료버튼
            #/html/body/div/form/div[1]/div[4]/div/button
            #결재안됨 버튼
            #/html/body/div[2]/div[2]/div/div/div/div/div/div/div/div[4]/button


            #결재완료버튼
            #//*[@id="payDoneBtn"]

            #//*[@id="termsSection"]/div/div[1]/div/label/span


            #결재완료 나이키 페이지
            #타이틀 "주문완료"
            #/html/body/section/section/section/article/article/div/h2/span
            #URL
            #https://www.nike.com/kr/launch/confirmation
        
    def payment(self):
        self.driver.implicitly_wait(3)
        # 결제

        while True:
            try:
                iframe = self.driver.find_element_by_xpath("/html/body/div[17]/iframe[2]")
                self.driver.switch_to.frame(iframe)
                break
            except NoSuchElementException:
                #ElementClickInterceptedException
                #보통 여기서 에러남 잠시후 다시
                self.driver.find_element_by_xpath('//*[@id="complete_checkout"]').click()

        self.driver.find_element_by_xpath('/html/body/div[4]/div/div[1]/button[2]').click()
        self.driver.implicitly_wait(2)
        self.driver.find_element_by_id('userPhone').send_keys(self.info['number'])
        self.driver.find_element_by_id('userBirth').send_keys(self.info['birth'])
        
        self.driver.find_element_by_xpath('//*[@id="userPost"]/fieldset/button').click()

        #driver.find_element_by_xpath('/html/body/div[4]/div/button').click()
        print('결재시도 성공')
        bot.sendMessage(chat_id=chat_id, text='결재 요청하였습니다.\n 결재를 완료해주세요.')
        while True:
            try:
                currentUrl = self.driver.current_url
                if '/confirmation' in currentUrl:
                    print("구매완료")
                    break;
                BuyBtn = self.driver.find_element_by_id('/html/body/div[4]/div/button')
                BuyBtn.click()
                break
            except NoSuchElementException:
                print("결재완료 버튼 클릭 시도중")
            except Exception as e:
                print("구매완")
                break

def wait_until_clickable(driver, xpath=None, class_name=None, el_id=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
    elif el_id:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.ID, el_id)))


def wait_until_visible(driver, xpath=None, class_name=None, el_id=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
    elif el_id:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, el_id)))
        
def wait_until_present(driver, xpath=None, class_name=None, el_id=None, duration=10000, frequency=0.01):
    if xpath:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.XPATH, xpath)))
    elif class_name:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    elif el_id:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.ID, el_id)))

def exit_gracefully():
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    signal.signal(signal.SIGINT, exit_gracefully)


#래플
# //*[@id="checkTerms"]/label
#//*[@id="optionPrivacy"]/label
#//*[@id="selectSize"]
#드로우 버튼
#//*[@id="btn-login"]
#드로우 결과확인
#//*[@id="btn-drawiswin"]
#/html/body/div[1]/div/div[1]/div[2]/div[1]/section/div[2]/aside/div[2]/div[3]


#no stocks quantity button
#/html/body/div[21]/div/div/div[2]/button

#no stock quantity msg
#/html/body/div[21]/div/div/div[1]

#no stock quantity popup
#/html/body/div[21]

#선택된 재고가없습니다. 팝업 div
#/html/body/div[17]

#팝업내 컨텐츠 내용
#/html/body/div[17]/div/div/div[1]

#AREA, 취소, 확인 버튼
#/html/body/div[17]/div/div/div[2]
#/html/body/div[17]/div/div/div[2]/button[1]
#/html/body/div[17]/div/div/div[2]/button[2]

#PG사 점검시간 Alert
#popup
#/html/body/div[18]
#내용
#/html/body/div[18]/div/div/div[1]
#확인버튼
#/html/body/div[18]/div/div/div[2]/button

if __name__ == "__main__":
    url = 'https://www.nike.com/kr/launch/'

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


    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    
    nike = Nike(info=info,proxy=None)
    browser_thread1 = threading.Thread(target=nike.run)
    browser_thread1.start()

    #nike2 = Nike(info=info2,proxy=None)
    #browser_thread12 = threading.Thread(target=nike2.run)
    #browser_thread12.start()
