#!/bin/bash

rm /tmp/pipe
rm ~/.mplayer/mplayer.log
rm ~/.mplayer/mplayer-err.log

sleep 1

mkfifo /tmp/pipe

find "$1" -type f \( -iname \*.mp3 \
                  -o -iname \*.flac \
                  -o -iname \*.wav \
                  -o -iname \*.mpc \
                  -o -iname \*.wv \
                  -o -iname \*.ape \
                  -o -iname \*.ogg \) \
                  | sort > mplayer_playlist.m3u


mplayer -vo null -ao alsa:device=plughw=2.0 -playlist mplayer_playlist.m3u -input file=/tmp/pipe -slave -idle -quiet -loop 0 > /tmp/mlog.txt &> ~/.mplayer/mplayer.log 2> ~/.mplayer/mplayer-err.log

