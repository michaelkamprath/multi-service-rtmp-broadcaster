FROM alpine:3
MAINTAINER Michael Kamprath "https://github.com/michaelkamprath"

ARG NGINX_VERSION=1.17.9
ARG RTMP_REPO=uizaio
ARG RTMP_MODULE_VERSION=1.4.0.4

RUN set -x \
 && addgroup -S stunnel \
 && adduser -S -D -H -h /dev/null -s /sbin/nologin -G stunnel -g stunnel stunnel \
 && echo "http://dl-3.alpinelinux.org/alpine/edge/testing/" >> /etc/apk/repositories \
 && apk update \
 && apk add --no-cache --update stunnel ca-certificates \
 && apk add --no-cache pcre openssl ffmpeg stunnel gettext \
 && apk add --no-cache --virtual build-deps build-base pcre-dev openssl-dev zlib zlib-dev wget make \
 && wget -O nginx-${NGINX_VERSION}.tar.gz http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
 && tar -zxvf nginx-${NGINX_VERSION}.tar.gz \
 && wget -O nginx-rtmp-module-${RTMP_MODULE_VERSION}.tar.gz https://github.com/${RTMP_REPO}/nginx-rtmp-module/archive/${RTMP_MODULE_VERSION}.tar.gz \
 && tar -zxvf nginx-rtmp-module-${RTMP_MODULE_VERSION}.tar.gz \
 && cd nginx-${NGINX_VERSION} \
 && export CFLAGS=-Wno-error \
 && ./configure --with-http_ssl_module --add-module=../nginx-rtmp-module-${RTMP_MODULE_VERSION} \
 && make \
 && make install \
 && apk del build-deps \
 && mkdir -p /var/www/html/recordings \
 && mkdir -p /var/run/stunnel/ \
 && chown nobody:nobody -R /var/www/html \
 && chown stunnel:stunnel /var/run/stunnel/

COPY index.html /usr/local/nginx/html/
COPY nginx-conf/nginx-conf-*.txt /
COPY launch-nginx-server.sh launch-nginx-server.sh
COPY stunnel-conf/etc-default-stunnel /etc/default/stunnel
COPY stunnel-conf/etc-stunnel-conf.d-fb.conf /etc/stunnel/conf.d/fb.conf
COPY stunnel-conf/etc-stunnel-stunnel.conf /etc/stunnel/stunnel.conf

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /usr/local/nginx/logs/access.log
RUN ln -sf /dev/stderr /usr/local/nginx/logs/error.log

RUN cp /nginx-rtmp-module-${RTMP_MODULE_VERSION}/stat.xsl /usr/local/nginx/html/

EXPOSE 1935
EXPOSE 80

STOPSIGNAL SIGTERM

CMD ["/bin/sh", "/launch-nginx-server.sh"]
