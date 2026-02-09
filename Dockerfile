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
