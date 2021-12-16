# syntax=docker/dockerfile:1
FROM alpine:3.14

WORKDIR /app
RUN apk add --no-cache bash\
                       python3 \
                       py3-pip \
                       gcc \
                       libcurl \
                       python3-dev \
                       libc-dev \
                       && rm -rf /var/cache/apk/*
RUN set -ex && apk --no-cache add sudo
RUN apk add --no-cache wiringpi
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
COPY . .
CMD [ "python3", "run.py" ]


# FROM python:3.8

# WORKDIR /app
# RUN apt update && apt install -y sudo && apt install -y wiringpi
# COPY requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt
# COPY . .
# CMD [ "python3", "run.py" ]