from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from time import sleep
from processor import Processor
from config import *

PLATFORM = 'Android'
DEVICE_NAME = 'santoni'
APP_PACKAGE = 'com.tencent.mm'
APP_ACTIVITY = '.ui.LaucherUI'

DRIVER_SERVER = 'http://localhost:4723/wd/hub'
TIMEOUT = 300

MONGO_URL = 'localhost'
MONGO_DB = 'moments'
MONGO_COLLECTION = 'moments'

PHONE = ''
PASSWORD = ''

#滑动点
FLICK_START_X = 300
FLICK_START_Y = 300
FLICK_DISTANCE = 700

SCROLL_SLEEP_TIME = 1

#新建一个moments类
class Moments():
	#初始化配置，如驱动的配置，延时等待配置，MongoDB连接配置
	def __init__(self):
		self.desired_caps = {
			'platformName':PLATFORM,
			'deviceName':DEVICE_NAME,
			'appPackage':APP_PACKAGE,
			'appActivity':APP_ACTIVITY
		}
		self.driver = webdriver.Remote(DRIVER_SERVER,self.desired_caps)
		self.wait = WebDriverWait(self.driver,TIMEOUT)
		self.client = MongoClient(MONGO_URL)
		self.db = self.client[MONGO_DB]
		self.collection = self.db[MONGO_COLLECTION]
		#处理器
		self.processor = Processor()

#登陆
def login(self):
	login = self.wait.until(EC.presence_of_element_located((By.ID,'com.tencent.mm:id/d1w')))
	login.click()
	phone = self.wait.until(EC.presence_of_element_located((By.ID,'com.tencent.mm:id/hx')))
	phone.set_text(PHONE)
	next = self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/ak_')))
	next.click()
	password = self.wait.until(EC.presence_of_element_located((By.ID,'com.tencent.mm:id/hx')))
	password.set_text(PASSWORD)
	submit = self.wait.until(EC.element_to_be_clickable((By.ID,'com.tencent.mm:id/ak_')))
	submit.click()

#进入微信
def enter(self):
	#选项卡
	tab = self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="selectedElementContainer"]/div/div[2]/i')))
	tab.click()
	#朋友圈
	moments = self.wait.until(EC.presence_of_element_located((By.ID,'')))
	moments.click()

#爬取信息
def crawl(self):
	while True:
		#当前页面显示的所有状态
		items = self.wait.unitl(EC.presence_of_element_located((By.XPATH,'')))
		#上滑
		self.driver.swipe(FLICK_START_X,FLICK_START_Y + FLICK_DISTANCE,FLICK_START_X,FLICK_START_Y)
		#遍历每条状态
		for item in items:
			try:
				#名字
				nickname = item.find_element_by_id('').get_attribute('')
				#正文
				content = item.find_element_by_id('').get_attribute('')
				#日期
				date = item.find_element_by_id('').get_attribute('')
				#处理日期
				date = self.processor.date(date)
				print(nickname,content,date)
				data = {
					'nickname':nickname,
					'content':content,
					'date':date,
				}
				#插入MongoDB
				self.collection.update({'nickname':naickname,'content':content},{'$set':data},True)
				sleep(SCROLL_SLEEP_TIME)
			except NoSuchElementException:
				pass

def main(self):
	#登陆
	self.login()

	#进入朋友圈
	self.enter()
	
	#爬取
	self.crawl()

if __name__ == '__main__':
	moments = Moments()
	moments.mian()






