FROM python:3.6.6-alpine3.8

RUN apk update \
    && apk upgrade \
    && apk add \
        build-base~=0.5 \
        postgresql-dev~=10.5

WORKDIR /opt/ttc/subway_times/

# Cop requirements file
COPY ./requirements.txt /opt/ttc/subway_times/

# Install dependencies
RUN pip install -r requirements.txt

# Copy source code
COPY . /opt/ttc/subway_times/

ENTRYPOINT ["python", "ttc_api_scraper.py", "--settings=db-docker.cfg"]
CMD ["--help"]
