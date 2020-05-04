#!/usr/bin/env sh

# set the password from environment variable
export DOLLAR='$'
envsubst < base-nginx.conf >  /usr/local/nginx/conf/nginx.conf

# start stunnel
/usr/bin/stunnel &

# append nginx conf with RTMP Configuration
python3 /rtmp-conf-generator.py /rtmp-configuation.json >> /usr/local/nginx/conf/nginx.conf

# finally, launch nginx
/usr/local/nginx/sbin/nginx -g "daemon off;"
