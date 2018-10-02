Backend P1: Video Thumbnailer
===================

How to Deploy on Docker

	1. In project dir, run "docker-compose up --build --scale worker=<worker number>"
	2. For Test: echo '{ "bucket": <bucketname>, "object": <objectname>, "output": <downloaded video output file>, "gif_filename": <gif_filename>, "start": <start time> }' | http POST localhost:5000/gif
