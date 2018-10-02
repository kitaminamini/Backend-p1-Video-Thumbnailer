import requests
import hashlib


BASE_URL = 'http://127.0.0.1:8280'
STATUS_OK = requests.codes['ok']
STATUS_BAD_REQUEST = requests.codes['bad_request']
STATUS_NOT_FOUND = requests.codes['not_found']

def test_uploading():
	resp = requests.post(BASE_URL + '/giftest?create')
	resp = requests.post(BASE_URL + '/giftest/BT-42.mp4?create')
	with open('../BT-42.mp4', 'rb') as data:
		D = data.read()
		resp = requests.put(url=BASE_URL+'/giftest/BT-42.mp4?partNumber=1',
						data=D,
						headers={'Content-Length': str(len(D)), 'Content-MD5': hashlib.md5(D).hexdigest()})
		assert resp.status_code == STATUS_OK

	resp = requests.post(BASE_URL+'/giftest/BT-42.mp4?complete')
	assert resp.status_code == STATUS_OK



def test_full_download():
	# with open('../BT-42.mp4', 'rb') as data:
	# 	D = data.read()
	# 	realMD5 = hashlib.md5(D).hexdigest()
	headers = {'Range': 'bytes=0-'}
	resp = requests.get(BASE_URL + '/giftest/BT-42.mp4', headers=headers, stream=True)
	assert resp.status_code == STATUS_OK

	with open('./out.mp4', 'wb') as handle:
		for block in resp.iter_content(2048):
			handle.write(block)