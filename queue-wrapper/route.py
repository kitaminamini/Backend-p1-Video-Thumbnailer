import os
import json
import redis
import requests
import logging
from flask import Flask, jsonify, request


SOS_URL = 'http://sos:8280'
QUEUE_URL = 'http://queue-wrapper:5000'
SOS_OUTER_URL = 'http://localhost:8280'
SOS_PORT = '8280'
STATUS_OK = requests.codes['ok']
STATUS_BAD_REQUEST = requests.codes['bad_request']
STATUS_NOT_FOUND = requests.codes['not_found']
VIDEO_EXTENSION = ["mp4", "mov", "avi"]
LOG = logging
LOG.basicConfig(
    level=LOG.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)


class RedisResource:
    REDIS_QUEUE_LOCATION = os.getenv('REDIS_QUEUE', 'localhost')
    QUEUE_NAME = 'queue:thumbnail'

    host, *port_info = REDIS_QUEUE_LOCATION.split(':')
    port = tuple()
    if port_info:
        port, *_ = port_info
        port = (int(port),)

    conn = redis.Redis(host=host, *port)


@app.route('/gif', methods=['POST'])
def post_gif_job():
    body = request.json
    json_packed = json.dumps(body)
    LOG.info(json_packed)
    print('packed:', json_packed)
    is_valid_request = checkRequest('/gif', json_packed)
    if is_valid_request:
        RedisResource.conn.rpush(
            RedisResource.QUEUE_NAME,
            json_packed)

        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'BAD_REQUEST'})


@app.route('/all_gifs/<bucketName>', methods=['GET'])
def get_all_gif(bucketName):
    resp = requests.get(SOS_URL + '/' + bucketName + '?list')
    if resp.status_code != STATUS_OK:
        return jsonify({'status': 'NOT_FOUND'})
    else:
        result = {}
        res_body = resp.json()
        for key in res_body["objects"]:
            obj = res_body["objects"][key]["name"]
            filename, extension = obj.rsplit('.', 1)
            if extension.lower() == "gif":
                result[obj] = SOS_OUTER_URL + '/' + bucketName + '/' + obj
        return jsonify(result)

@app.route('/gifs_for_videos/<bucketName>', methods=['POST'])
def post_gif_jobs_all(bucketName):
    resp = requests.get(SOS_URL + '/' + bucketName + '?list')
    if resp.status_code != STATUS_OK:
        return jsonify({'status': 'BAD_REQUEST'})
    else:
        res_body = resp.json()
        for key in res_body["objects"]:
            obj = res_body["objects"][key]["name"]
            filename, extension = obj.rsplit('.', 1)
            if extension.lower() in VIDEO_EXTENSION:
                di = {"bucket": bucketName, "object": obj, "gif_filename": filename+".gif", "start": 0}
                res = requests.post(QUEUE_URL + '/gif', json=di)
        return jsonify({'status': 'OK'})


def checkRequest(urlpath, strBody):
    if urlpath == '/gif':
        body = json.loads(strBody)
        LOG.info(type(body))
        if "gif_filename" in body and "bucket" in body and "object" in body:
            resp = requests.get(SOS_URL + '/' + body["bucket"] + '?list')

            if resp.status_code != STATUS_OK:
                return False

            else:
                res_body = resp.json()
                key = body["object"].replace(".", "/")
                if key in res_body["objects"]:
                    return True
        else:
            return False

    else:
        return False


