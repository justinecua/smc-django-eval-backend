# Switched to python:3.11-slim.
# Old Ubuntu + Python 3.9 + OpenSSL broke ReportLab PDF (md5 error) when generating PDF files.
# This new Dockerfle fixes PDF generation 

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /api
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*
COPY smcEvalProject/requirements.txt /api/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt
COPY . /api/
EXPOSE 8000

#---------OLD Dockerfile---------

# FROM ubuntu:20.04
# RUN apt-get update
# RUN apt-get install -y software-properties-common
# RUN add-apt-repository ppa:deadsnakes/ppa
# RUN apt-get install -y python3.9
# RUN python3.9 --version
# RUN apt-get install -y python3.9-dev build-essential
# RUN apt-get install -y python3-dev default-libmysqlclient-dev build-essential
# RUN apt-get install -y libssl1.1
# RUN apt-get install -y libssl-dev
# RUN apt-get install -y libmysqlclient-dev
# RUN ln /usr/bin/python3.9 /usr/bin/python
# RUN apt-get install -y python3-pip
# RUN pip install --upgrade pip
# ENV PYTHONUNBUFFERED=1
# WORKDIR /api
# COPY smcEvalProject/requirements.txt /api/requirements.txt
# RUN pip install -r requirements.txt
# COPY . /api/
# RUN apt-get install -y apt-utils vim curl
# EXPOSE 8000