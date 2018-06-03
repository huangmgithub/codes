import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing.pool import Pool

base_url = 'https://www.toutiao.com/search_content/?'

headers = {
	'Host': 'www.toutiao.com',
	'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
	'x-requested-with': 'XMLHttpRequest'
}

def get_page(offset):
	params = {
	'offset':offset,
	'format':'json',
	'keyword':'街拍',
	'autoload':'true',
	'count':'20',
	'cur_tab':'1',
	'from':'search_tab',
	}

	url = base_url + urlencode(params)

	try:
		response = requests.get(url=url,headers=headers)
		response.raise_for_status()
		return response.json()
	except requests.ConnectionError:
		print('获取网页失败')

def get_images(json):
	if json:
		for item in json.get('data'):
			image_list = item.get('image_list')
			title = item.get('title')
			if image_list:
				for image in image_list:
					print(image)
					yield {
						'image': image.get('url'),
						'title': title
					}
	
def save_image(item):
	if not os.path.exists(item.get('title')):
		os.mkdir(item.get('title'))
	try:
		response = requests.get('http:' + item.get('image'))
		response.raise_for_status()
		file_path = '{0}/{1}.{2}'.format(item.get('title'),md5(response.content).hexdigest(),'jpg')
		if not os.path.exists(file_path):
			with open(file_path,'wb') as f:
				f.write(response.content)
		else:
			print('已下载')
	except requests.ConnectionError:
		print('存储失败')

def main(offset):
	json = get_page(offset)
	for item in get_images(json):
		print(item)
		save_image(item)

if __name__ == '__main__':
	pool = Pool()
	groups = ([x * 20 for x in range(1,40+1)])
	pool.map(main,groups)
	pool.close()
	pool.join()






					





