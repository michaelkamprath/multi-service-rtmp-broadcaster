FROM alpine:3
MAINTAINER Michael Kamprath "https://github.com/michaelkamprath"

ARG NGINX_VERSION=1.17.9
ARG RTMP_REPO=defanator
ARG RTMP_MODULE_VERSION=fix-build-with-gcc8

RUN set -x \
 && addgroup -g 82 -S www-data \
 && adduser -u 82 -D -S -G www-data www-data \
 && apk add --no-cache pcre openssl ffmpeg stunnel gettext \
 && apk add --no-cache --virtual build-deps build-base pcre-dev openssl-dev zlib zlib-dev wget make \
 && wget -O nginx-${NGINX_VERSION}.tar.gz http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
 && tar -zxvf nginx-${NGINX_VERSION}.tar.gz \
 && wget -O nginx-rtmp-module-${RTMP_MODULE_VERSION}.tar.gz https://github.com/${RTMP_REPO}/nginx-rtmp-module/archive/${RTMP_MODULE_VERSION}.tar.gz \
 && tar -zxvf nginx-rtmp-module-${RTMP_MODULE_VERSION}.tar.gz \
 && cd nginx-${NGINX_VERSION} \
 && ./configure --with-http_ssl_module --add-module=../nginx-rtmp-module-${RTMP_MODULE_VERSION} \
 && make \
 && make install\
 && apk del build-deps \
 && mkdir -p /var/www/html/recordings \
 && chown www-data:www-data -R /var/www/html

COPY index.html /usr/local/nginx/html/
COPY nginx-conf/nginx-conf-*.txt /
COPY launch-nginx-server.sh launch-nginx-server.sh
COPY stunnel-conf/etc-default-stunnel4 /etc/default/stunnel4
COPY stunnel-conf/etc-stunnel-conf.d-fb.conf /etc/stunnel/conf.d/fb.conf
COPY stunnel-conf/etc-stunnel-stunnel.conf /etc/stunnel/stunnel.conf

EXPOSE 1935
EXPOSE 80

STOPSIGNAL SIGTERM

CMD ["/bin/sh", "/launch-nginx-server.sh"]
