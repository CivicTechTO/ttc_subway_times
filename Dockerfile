FROM python:3.6.6-alpine3.8

RUN apk update \
    && apk upgrade \
    && apk add \
        build-base~=0.5 \
        postgresql-dev~=10.5

WORKDIR /opt/ttc/subway_times/

# Copy requirements file
COPY ./requirements.txt /opt/ttc/subway_times/

# Install dependencies
RUN pip install -r requirements.txt

# Copy source code
COPY src /opt/ttc/subway_times/src
COPY db-docker.cfg db-docker.cfg

ENV PYTHONPATH src

ENTRYPOINT ["python", "-m", "ttc_api_scraper.ttc_api_scraper", "-d", "db-docker.cfg", "scrape", "--postgres"]