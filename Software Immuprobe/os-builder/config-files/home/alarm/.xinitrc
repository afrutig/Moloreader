#!/bin/bash

#IP=/home/alarm/immuprobe-git/software
IP=/opt/immuprobe


istouch=$(xrandr | grep 800x480) # simple test for 800x480 screen

if [ "$istouch" ]; then
	cursor=no
else
	cursor=yes
fi

# start the window manager
matchbox-window-manager -use_titlebar no -use_cursor $cursor &
xterm -bg black -fg blue -e 'worms -n 1 -d 10 -f' && xterm -bg black -fg green &
#ristretto -f $IP/resources/immuprobe_icon_v2_black.svg &

firefox  $IP/gui/splash.html &
bash -c "cd $IP/gui; ./server.sh" && firefox localhost:5000 &


#nm-connection-editor &

wait
