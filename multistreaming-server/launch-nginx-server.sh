#!/usr/bin/env sh

# set the password from environment variable
export DOLLAR='$'
envsubst < base-nginx.conf >  /usr/local/nginx/conf/nginx.conf

# append nginx conf with RTMP Configuration
python3 /rtmp-conf-generator.py /rtmp-configuration.json /nginx-template.conf.j2 >> /usr/local/nginx/conf/nginx.conf
if [ $? -ne 0 ]; then
  echo "ERROR encountered when generating RTMP configuration."
  exit 1
fi

# finally, launch nginx
/usr/local/nginx/sbin/nginx -g "daemon off;"
