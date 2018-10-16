#!/usr/bin/env python3
import hashlib
import os
import logging
import json
import uuid
import redis
import requests
import subprocess

SOS_URL = 'http://sos:8280'
SOS_PORT = '8280'
STATUS_OK = requests.codes['ok']
STATUS_BAD_REQUEST = requests.codes['bad_request']
STATUS_NOT_FOUND = requests.codes['not_found']

LOG = logging
REDIS_QUEUE_LOCATION = os.getenv('REDIS_QUEUE', 'localhost')
QUEUE_NAME = 'queue:thumbnail'

INSTANCE_NAME = uuid.uuid4().hex

LOG.basicConfig(
    level=LOG.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def watch_queue(redis_conn, queue_name, callback_func, timeout=30):
    active = True

    while active:
        # Fetch a json-encoded task using a blocking (left) pop
        packed = redis_conn.blpop([queue_name], timeout=timeout)

        if not packed:
            # if nothing is returned, poll a again
            continue

        _, packed_task = packed

        # If it's treated to a poison pill, quit the loop
        if packed_task == b'DIE':
            active = False
        else:
            task = None
            try:
                task = json.loads(packed_task.decode("utf-8"))
            except Exception:
                LOG.exception('json.loads failed')
            if task:
                callback_func(task)


# def execute_factor(log, task):
#     number = task.get('number')
#     if number:
#         number = int(number)
#         log.info('Factoring %d', number)
#         factors = [trial for trial in range(1, number + 1) if number % trial == 0]
#         log.info('Done, factors = %s', factors)
#     else:
#         log.info('No number given.')


def execute_thumbnailing(log, task):
    # step 1: Download video from SOS
    log.info("in step 1")
    log.info(task)
    bucket = task.get('bucket')
    obj = task.get('object')
    filepath = "/"+bucket+"/"+obj
    # headers = task.get('headers')
    try:
        headers = {'Range': 'bytes=0-'} # for now TODO change it
        log.info(SOS_URL + filepath)
        resp = requests.get(SOS_URL + filepath, headers=headers, stream=True)
        if resp.status_code == STATUS_OK:
            output = obj
            with open('./' + output, 'wb') as handle:
                for block in resp.iter_content(2048):
                    handle.write(block)

            # step 2: Generate gif from video
            log.info("in step 2")
            gif_filename = task.get('gif_filename')
            start_time = task.get('start')
            try:
                subprocess.call(["chmod", "+x", "videoToGif.sh"])
                subprocess.call(["./videoToGif.sh", "./"+output, gif_filename, str(start_time)])
            except subprocess.SubprocessError as e:
                log.info(str(e)+": Failed to run gif generator")
                return
                # return execute_thumbnailing(log, task)

            # step 3: Upload gif to SOS
            log.info("in step 3")
            resp = requests.post(SOS_URL + "/"+bucket+"/"+gif_filename+"?create")
            if resp.status_code != STATUS_OK:
                requests.delete(SOS_URL + "/"+bucket+"/"+gif_filename+"?delete")
                requests.post(SOS_URL + "/" + bucket + "/" + gif_filename + "?create")
            data = open('./'+gif_filename, 'rb').read()
            resp = requests.put(url=SOS_URL + "/"+bucket+"/"+gif_filename+'?partNumber=1', data=data,
                        headers={'Content-Length': str(len(data)), 'Content-MD5': hashlib.md5(data).hexdigest()})
            if resp.status_code == STATUS_OK:
                requests.post(SOS_URL + "/" + bucket + "/" + gif_filename + "?complete")
                log.info("====Conpleted uploading "+gif_filename+"====")

    except (ConnectionError, TimeoutError) as e:
        log.info(str(e)+": Failed to connect to SOS")



def main():
    LOG.info('Starting a worker...')
    LOG.info('Unique name: %s', INSTANCE_NAME)
    host, *port_info = REDIS_QUEUE_LOCATION.split(':')
    port = tuple()
    if port_info:
        port, *_ = port_info
        port = (int(port),)

    named_logging = LOG.getLogger(name=INSTANCE_NAME)
    named_logging.info('Trying to connect to %s [%s]', host, REDIS_QUEUE_LOCATION)
    redis_conn = redis.Redis(host=host, *port)
    watch_queue(
        redis_conn,
        QUEUE_NAME,
        lambda task_descr: execute_thumbnailing(named_logging, task_descr))


if __name__ == '__main__':
    main()
