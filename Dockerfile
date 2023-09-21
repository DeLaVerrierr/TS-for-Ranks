FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y python3
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/


RUN apt-get update && apt-get install -y sqlite3

RUN python app/manage.py collectstatic --noinput
RUN python app/manage.py createsuperuser --noinput --username=adminweb --email=admin@example.com

EXPOSE 8000

RUN useradd -ms /bin/bash app
USER app

CMD ["python", "app/manage.py", "runserver", "0.0.0.0:8000"]