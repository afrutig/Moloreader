#!/bin/bash

# start the twistd server
rm -f twistd.pid
truncate -s 0 twistd.log
twistd web --port 5000 --wsgi server.app
