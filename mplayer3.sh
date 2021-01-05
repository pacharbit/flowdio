#!/bin/bash

rm /tmp/pipe
rm /tmp/aufifo
rm ~/.mplayer/mplayer.log
rm ~/.mplayer/mplayer-err.log

sleep 2

mkfifo /tmp/pipe
mkfifo /tmp/aufifo

find "$1" -type f \( -iname \*.mp3 \
                  -o -iname \*.flac \
                  -o -iname \*.wav \
                  -o -iname \*.mpc \
                  -o -iname \*.wv \
                  -o -iname \*.ape \
                  -o -iname \*.ogg \) \
                  | sort > mplayer_playlist.m3u

AUDIODEV=hw:2,0 play -t raw -r 44100 -b 16 -c 2 -e signed-integer  /tmp/aufifo &

mplayer -vo null -ao pcm:nowaveheader:file=/tmp/aufifo -playlist mplayer_playlist.m3u -input file=/tmp/pipe -slave -idle -quiet > /tmp/mlog.txt &> ~/.mplayer/mplayer.log 2> ~/.mplayer/mplayer-err.log
