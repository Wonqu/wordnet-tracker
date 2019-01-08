# Upgrade to 3.7 when Celery is available for it https://github.com/celery/celery/issues/4500
FROM python:3.6
LABEL maintainer="Tomasz Naskręt <tomasz.naskret@pwr.edu.pl>"

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN pip install -e .  # docker on windows eats last few characters of a file so a comment is necessary (sadly...)
