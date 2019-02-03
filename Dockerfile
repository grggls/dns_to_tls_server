FROM python:alpine
ARG STUB
ENV STUB ${STUB}
WORKDIR /tmp
RUN apk --update add --no-cache alpine-sdk libcurl curl-dev curl git knot-utils && \
    git clone https://github.com/curl/doh && \
    cd doh && make && mv /tmp/doh/doh /usr/local/bin/doh && \
    rm -rf /tmp/doh

WORKDIR /srv
ADD ./requirements.txt /srv
RUN pip install -r requirements.txt
ADD . /srv

RUN addgroup -g 942 srv && \
    adduser -S -u 942 -h /srv/ -s /sbin/nologin -D -H srv srv
USER srv

CMD python3 dnstotls_server.py -p 8053 -c 3 -s ${STUB}
EXPOSE 8053
