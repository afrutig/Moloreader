#!/bin/bash

CMD=$1

case $CMD in
	"start")
		killall raspivid
		/opt/vc/bin/raspivid -t 0 -rot 180 -w 800 -h 800 &
	;;
	"stop")
		killall raspivid
	;;
	*)
		echo 'Invalid command. Use start or stop.'
	;;
esac
