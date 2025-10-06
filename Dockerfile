FROM python:3.12-slim

WORKDIR /code

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

ENV DJANGO_SETTINGS_MODULE=smcEvalProject.settings

EXPOSE 8000

CMD ["gunicorn", "smcEvalProject.wsgi:application", "--bind", "0.0.0.0:8000"]
