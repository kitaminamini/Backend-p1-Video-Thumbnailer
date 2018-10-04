import os
import json
import requests
import logging
from flask import Flask, jsonify, request, render_template


SOS_URL = 'http://sos:8280'
SOS_OUTER_URL = 'http://localhost:8280'
SOS_PORT = '8280'
THUMBNAILER_URL = 'http://queue-wrapper:5000'
THUMBNAILER_PORT = '5000'
STATUS_OK = requests.codes['ok']
STATUS_BAD_REQUEST = requests.codes['bad_request']
STATUS_NOT_FOUND = requests.codes['not_found']
LOG = logging
LOG.basicConfig(
    level=LOG.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

VIDEO_EXTENSION = ["mp4", "mov", "avi"]
THUMBNAILER_INPUT = ["bucket", "object", "gif_filename", "start"]


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<bucketName>/show_all_videos', methods = ['POST', 'GET'])
def show_all_videos(bucketName):
    resp = requests.get(SOS_URL + '/' + bucketName + '?list')
    if resp.status_code != STATUS_OK:
        return False
    else:
        res_body = resp.json()
        result = []
        for key in res_body["objects"]:
            obj = res_body["objects"][key]["name"]
            filename, extension = obj.rsplit('.', 1)
            if extension.lower() in VIDEO_EXTENSION:
                result.append(obj)
        return render_template("all_videos.html", result=result, bucket=bucketName)


@app.route('/gif', methods=['POST'])
def submit_job():
    form = request.form
    LOG.info(form)
    body = request.form.to_dict(flat=True)
    #     {
    #     key: value[0] if len(value) == 1 else value
    #     for key, value in request.form.iterlists()
    # }
    LOG.info(body)
    try:
        res = requests.post(THUMBNAILER_URL+'/gif', json=body)
        if res.json()['status'] != 'OK':
            return jsonify({'status': 'BAD_REQUEST'})
        else:
            return jsonify({'status': 'OK'})

    except (ConnectionError, TimeoutError) as e:
        return jsonify({'status': 'BAD_REQUEST'})


@app.route('/display', methods=['POST'])
def display_all_gif():
    result = {}
    form = request.form
    LOG.info(form)
    body = request.form.to_dict(flat=True)
    bucket = body["bucket"]
    resp = requests.get(SOS_URL + '/' + bucket + '?list')
    if resp.status_code != STATUS_OK:
        return False
    else:
        res_body = resp.json()
        for key in res_body["objects"]:
            obj = res_body["objects"][key]["name"]
            filename, extension = obj.rsplit('.', 1)
            if extension.lower() == "gif":
                result[obj] = SOS_OUTER_URL + '/' + bucket + '/' + obj
    return render_template('display.html', bucket=bucket, result=result)

if __name__ == '__main__':
    app.run(debug=True)


