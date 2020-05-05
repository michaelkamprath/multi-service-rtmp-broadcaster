#!/usr/bin/env sh
export DOLLAR='$'

# construct the nginx.conf based on environment variable definitions

envsubst < nginx-conf-prefix.txt >  /usr/local/nginx/conf/nginx.conf

if [ $MULTISTREAMING_KEY_FACEBOOK ]; then
	envsubst < nginx-conf-facebook.txt >>  /usr/local/nginx/conf/nginx.conf
	if [ $FACEBOOK_TRANSCODE ]; then
		sed -e "s/##PUSH_FACEBOOK_TRANSCODE_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
	else
		sed -e "s/##PUSH_FACEBOOK_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
	fi
	/usr/bin/stunnel &
fi

if [ $MULTISTREAMING_KEY_INSTAGRAM ]; then
	envsubst < nginx-conf-instagram.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_INSTAGRAM_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
	/usr/bin/stunnel &
fi

if [ $MULTISTREAMING_KEY_TWITCH ]; then
	envsubst < nginx-conf-twitch.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_TWITCH_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
fi

if [ $MULTISTREAMING_KEY_YOUTUBE ]; then
	envsubst < nginx-conf-youtube.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_YOUTUBE_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
fi

if [ $MULTISTREAMING_KEY_PERISCOPE ]; then
	if [ !$PERISCOPE_REGION_ID ]; then
		export PERISCOPE_REGION_ID='ca'
	fi
	envsubst < nginx-conf-periscope.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_PERISCOPE_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
fi

if [ $MULTISTREAMING_KEY_CUSTOM ]; then
	envsubst < nginx-conf-custom.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_CUSTOM_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
fi

if [ $MULTISTREAMING_KEY_MICROSOFTSTREAM ]; then
	export MICROSOFTSTREAMRTMP=${MULTISTREAMING_KEY_MICROSOFTSTREAM%/live/*}
	export MICROSOFTSTREAMAPPNAME=live/${MULTISTREAMING_KEY_MICROSOFTSTREAM#*/live/}
	envsubst < nginx-conf-microsoftstream.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_MICROSOFTSTREAM_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
fi

if [ $MULTISTREAMING_ICECAST ]; then
	envsubst < nginx-conf-icecast.txt >>  /usr/local/nginx/conf/nginx.conf
	sed -e "s/##PUSH_ICECAST_MARKER##//g" -i /usr/local/nginx/conf/nginx.conf
fi

envsubst < nginx-conf-suffix.txt >>  /usr/local/nginx/conf/nginx.conf

# finally, launch nginx
/usr/local/nginx/sbin/nginx -g "daemon off;"
