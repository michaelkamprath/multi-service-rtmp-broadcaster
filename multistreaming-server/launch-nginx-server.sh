#!/usr/bin/env sh
export DOLLAR='$'

# construct the nginx.conf based on environment variable definitions

envsubst < nginx-conf-prefix.txt >  /usr/local/nginx/conf/nginx.conf

if [ $MULTISTREAMING_KEY_FACEBOOK ]; then
	envsubst < nginx-conf-facebook.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_FACEBOOK_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
	/usr/bin/stunnel4 &
fi

if [ $MULTISTREAMING_KEY_TWITCH ]; then
	envsubst < nginx-conf-twitch.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_TWITCH_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
fi

if [ $MULTISTREAMING_KEY_YOUTUBE ]; then
	envsubst < nginx-conf-youtube.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_YOUTUBE_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
fi

envsubst < nginx-conf-suffix.txt >>  /usr/local/nginx/conf/nginx.conf

# finally, launch nginx
/usr/local/nginx/sbin/nginx -g "daemon off;"
