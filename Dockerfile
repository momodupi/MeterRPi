# syntax=docker/dockerfile:1
FROM python:3.8-slim

WORKDIR /app
RUN apt-get update && apt-get install -y sudo && apt-get install -y gcc
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "run.py" ]