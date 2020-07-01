FROM python:3.7.8-alpine3.12

RUN apk add --virtual .build-dependencies \ 
            --no-cache \
            python3-dev \
            build-base \
            linux-headers \
            pcre

WORKDIR /var/www/ingaia-challenge
RUN mkdir -p /var/www/ingaia-challenge/app
COPY ./app /var/www/ingaia-challenge/app
COPY requirements.txt /var/www/ingaia-challenge
RUN pip3 install -r requirements.txt
WORKDIR /var/www/ingaia-challenge/app
RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

EXPOSE 8080
CMD ["uwsgi", "--ini", "/var/www/ingaia-challenge/app/wsgi.ini"]
