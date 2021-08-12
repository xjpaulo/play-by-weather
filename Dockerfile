FROM python:3.7.8-alpine3.12

RUN apk add --virtual .build-dependencies \ 
            --no-cache \
            python3-dev \
            build-base \
            linux-headers \
            pcre

WORKDIR /var/www/play-by-weather
RUN mkdir -p /var/www/play-by-weather/app
COPY ./app /var/www/play-by-weather/app
COPY requirements.txt /var/www/play-by-weather
RUN pip3 install -r requirements.txt
WORKDIR /var/www/play-by-weather/app
RUN apk del .build-dependencies && rm -rf /var/cache/apk/*

EXPOSE 8080
CMD ["uwsgi", "--ini", "/var/www/play-by-weather/app/wsgi.ini"]
