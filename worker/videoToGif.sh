#!/usr/bin/env bash

inputFile=$1
outputFile=$2
start=$3

mkdir frames
ffmpeg -y -ss $start -t 7 -i $inputFile -vf scale=640:480 -r 20 ./frames/ffout%03d.png
convert -delay 5 -loop 0 ./frames/ffout*.png $outputFile
rm -rf frames