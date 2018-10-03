import os
import json
import redis
import requests
from flask import Flask, jsonify, request


SOS_URL = 'http://sos:8280'
SOS_PORT = '8280'
STATUS_OK = requests.codes['ok']
STATUS_BAD_REQUEST = requests.codes['bad_request']
STATUS_NOT_FOUND = requests.codes['not_found']

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
def post_factor_job():
    body = request.json
    json_packed = json.dumps(body)
    print('packed:', json_packed)
    is_valid_request = checkRequest('/gif', json_packed)
    if is_valid_request:
        RedisResource.conn.rpush(
            RedisResource.QUEUE_NAME,
            json_packed)

        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'BAD_REQUEST'})



def checkRequest(urlpath, body):
    if urlpath == '/gif':
        if "output" in body and "gif_filename" in body and "bucket" in body and "object" in body:
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


