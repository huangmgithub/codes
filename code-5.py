from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
import pymongo

browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)
keyword = "ipad"

MONGO_URL = 'localhost'
MONGO_DB = 'taobao2'
MONGO_TABLE = 'products'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def index_page(page):
	try:
		url = 'https://www.taobao.com/?q=' + quote(keyword)
		browser.get(url)
		if page > 1:
			input = wait.until(
				EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.form > input')))

			submit = wait.until(
				EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
			input.clear()
			input.send_keys(page)
			submit.click()
		wait.until(
			EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page)))
		wait.until(
			EC.presence_of_element_located((By.CSS_SELECTOR,'.m-itemlist .items .item')))
		get_products()
	except TimeoutException:
		index_page(page)

def get_products():
	html = browser.page_source
	doc = pq(html)
	items = doc('.m-itemlist .items .item').items()
	for item in items:
		product = {
			'title':item.find('.title').text()
			'image':item.find('.pic img').attr('src')
			'price':item.find('.price').text()
			'deal':item.find('.deal-cnt').text()[:-3]
			'shop':item.find('.shop').text()
			'location':item.find('.location').text()
		}
		print(product)
		save_to_mongo(product)

def save_to_mongo(result):
	try:
		if db[MONGO_TABLE].insert(result):
			print('数据保存成功',result)
	except Exception:
		print('数据保存失败',result)

def main():
	total_page = 100
	for i in range(1,total_page + 1):
		index_page(i)
	broswer.close()

if __name__ == '__main__':
	main()


