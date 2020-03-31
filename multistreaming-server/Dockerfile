FROM ubuntu:bionic
MAINTAINER Michael Kamprath "https://github.com/michaelkamprath"

ARG NGINX_VERSION=1.17.9
ARG RTMP_MODULE_VERSION=1.2.1

RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y build-essential libpcre3 libpcre3-dev libssl-dev zlib1g zlib1g-dev ffmpeg \
                    locales less gettext-base wget \
                    gcc g++ make \
                    stunnel4 \
 && rm -rf /var/lib/apt/lists/* \
 && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

RUN wget -O nginx-${NGINX_VERSION}.tar.gz http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
 && tar -zxvf nginx-${NGINX_VERSION}.tar.gz \
 && wget -O nginx-rtmp-module-${RTMP_MODULE_VERSION}.tar.gz https://github.com/arut/nginx-rtmp-module/archive/v${RTMP_MODULE_VERSION}.tar.gz \
 && tar -zxvf nginx-rtmp-module-${RTMP_MODULE_VERSION}.tar.gz \
 && cd nginx-${NGINX_VERSION} \
 && ./configure --with-http_ssl_module --add-module=../nginx-rtmp-module-${RTMP_MODULE_VERSION} \
 && make \
 && make install

RUN mkdir -p /var/www/html/recordings \
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

CMD ["/bin/bash", "/launch-nginx-server.sh"]
