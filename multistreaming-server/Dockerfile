FROM jrottenberg/ffmpeg:4.3-alpine
MAINTAINER Michael Kamprath "https://github.com/michaelkamprath"

ARG NGINX_VERSION=1.19.2
ARG RTMP_REPO=uizaio
ARG RTMP_MODULE_VERSION=1.4.0.4
ARG TINI_VERSION=v0.19.0
ARG SUPERVISORD_VERSION=4.2.1
ARG PIPENV_PACKAGE_VERSION=2020.8.13

RUN set -x \
 && addgroup -S stunnel \
 && adduser -S -D -H -h /dev/null -s /sbin/nologin -G stunnel -g stunnel stunnel \
 && echo "//dl-cdn.alpinelinux.org/alpine/latest-stable/main/x86_64/" >> /etc/apk/repositories \
 && apk update \
 && apk add --no-cache --update stunnel ca-certificates \
 && apk add --no-cache pcre openssl stunnel gettext python3 \
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
 && cp /nginx-rtmp-module-${RTMP_MODULE_VERSION}/stat.xsl /usr/local/nginx/html/ \
 && apk del build-deps \
 && mkdir -p /var/www/html/recordings \
 && mkdir -p /var/run/stunnel/ \
 && chown nobody:nobody -R /var/www/html \
 && chown stunnel:stunnel /var/run/stunnel/ \
 && wget -O /tini https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-static \
 && chmod +x /tini \
 && pip3 install supervisor==${SUPERVISORD_VERSION} pipenv==${PIPENV_PACKAGE_VERSION}

COPY Pipfile Pipfile.lock /
RUN  pipenv install --system --deploy

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY stunnel-conf/etc-default-stunnel /etc/default/stunnel
COPY stunnel-conf/etc-stunnel-conf.d-fb.conf /etc/stunnel/conf.d/fb.conf
COPY stunnel-conf/etc-stunnel-conf.d-ig.conf /etc/stunnel/conf.d/ig.conf
COPY stunnel-conf/etc-stunnel-stunnel.conf /etc/stunnel/stunnel.conf

COPY index.html /usr/local/nginx/html/
COPY nginx-conf/nginx.conf /base-nginx.conf
COPY launch-nginx-server.sh launch-nginx-server.sh
COPY rtmp-conf-generator.py nginx-template.conf.j2 /

EXPOSE 1935
EXPOSE 80

STOPSIGNAL SIGTERM
ENTRYPOINT ["/tini", "--"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
