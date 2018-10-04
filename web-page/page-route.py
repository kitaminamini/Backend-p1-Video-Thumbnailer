import os
import json
import requests
import logging
import ast
from flask import Flask, redirect, url_for, jsonify, request, render_template

WEB_URL = 'http://localhost:9780'
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

@app.route('/show_all_videos', methods = ['POST'])
def show_all_videos():
    form = request.form
    LOG.info(form)
    body = request.form.to_dict(flat=True)
    bucketName = body["bucket"]
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
    LOG.info(body)
    try:
        res = requests.post(THUMBNAILER_URL+'/gif', json=body)
        if res.json()['status'] != 'OK':
            return jsonify({'status': 'BAD_REQUEST'})
        else:
            return jsonify({'status': 'OK'})

    except (ConnectionError, TimeoutError) as e:
        return jsonify({'status': 'BAD_REQUEST'})


@app.route('/display/<bucketname>', methods=['GET'])
def display_all_gif(bucketname):
    # form = request.form
    # LOG.info(form)
    # body = request.form.to_dict(flat=True)
    # bucket = body["bucket"]
    bucket = bucketname
    resp = requests.get(THUMBNAILER_URL + '/all_gifs/' + bucket)
    if resp.status_code != STATUS_OK:
        return jsonify({'status': 'BAD_REQUEST'})
    else:
        res_body = resp.json()
        return render_template('display.html', bucket=bucket, result=res_body)

@app.route('/delete/<bucketname>/<objectname>', methods=['GET'])
def delete_gif(bucketname, objectname):
    res_code = delete(bucketname, objectname)
    if res_code == STATUS_OK:
        return redirect(WEB_URL+"/display/"+bucketname)
    else:
        return jsonify({'status': 'BAD_REQUEST'})

@app.route('/delete_all/<bucketname>', methods=['POST'])
def delete_all_gif(bucketname):
    form = request.form
    LOG.info(form)
    body = request.form.to_dict(flat=True)
    LOG.info(body)
    for key in ast.literal_eval(body["object"]):
        res_code = delete(bucketname, key)
        if res_code != STATUS_OK:
            return jsonify({'status': 'BAD_REQUEST'})

    return redirect(WEB_URL+"/display/"+bucketname)

def delete(bucketname, objectname):
    resp = requests.delete(SOS_URL + '/' + bucketname + '/'+ objectname +'?delete')
    return resp.status_code

if __name__ == '__main__':
    app.run(debug=True)


