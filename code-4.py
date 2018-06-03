from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
import pymongo

client = pymongo.MongoClient()
db = client['weibo']
collection = db['weibo']

base_url = 'https://m.weibo.cn/api/container/getIndex?'

headers = {
	'Host': 'm.weibo.cn',
	'referer': 'https://m.weibo.cn/u/2830678474',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
	'x-requested-with': 'XMLHttpRequest'
}

def get_page(page):
	params = {
		'type':'uid',
		'value':'2830678474',
		'containerid':'1076032830678474',
		'page':page
	}
	url = base_url + urlencode(params)
	print(url)
	try:
		response = requests.get(url=url,headers=headers)
		response.raise_for_status()
		return response.json()
	except requests.ConnectionError as e:
		print('Error',e.args)

def parse_page(json):
	if json:
		items = json.get('data').get('cards')
		for item in items:
			item = item.get('mblog')
			weibo = {}
			weibo['id'] = item.get('id')
			weibo['text'] = pq(item.get('text')).text()
			weibo['attitudes'] = item.get('attitudes_count')
			weibo['comments'] = item.get('comments_count')
			weibo['reposts'] = item.get('reposts_count')
			yield weibo

def save_to_mongo(result):
 	try:
 		if collection.insert(result):
 			print('数据存储成功',result)
 	except:
 		print('数据存储失败',result)

def main():
	for page in range(1,11):
		json = get_page(page)
		results = parse_page(json)
		for result in results:
			print(result)
			save_to_mongo(result)

if __name__ == '__main__':
	main()
