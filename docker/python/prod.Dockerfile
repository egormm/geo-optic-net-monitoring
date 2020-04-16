FROM python:3.7-alpine as builder
MAINTAINER Makrushin Egor egormm@gmail.com

WORKDIR /usr/src/whitenet

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update && apk upgrade \
    && apk add \
        postgresql-client \
        postgresql-dev \
        musl-dev \
        gcc

# install dependencies
RUN pip install --upgrade pip
COPY ./docker/python/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/whitenet/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.7-alpine

# create directory for the app user
RUN mkdir -p /home/whitenet

# create the app user
RUN addgroup -S whitenet && adduser -S whitenet -G whitenet

# create the appropriate directories
ENV HOME=/home/whitenet
ENV APP_HOME=/home/whitenet/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install graphviz and geos dependencies
RUN apk update && apk upgrade \
    && apk add --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
        musl-dev \
        gcc \
    && apk add --repository http://dl-cdn.alpinelinux.org/alpine/edge/community \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
        gdal-dev \
        geos-dev \
        proj-dev \
    && apk add bash graphviz ttf-freefont


# install dependencies
COPY --from=builder /usr/src/whitenet/wheels /wheels
COPY --from=builder /usr/src/whitenet/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy entrypoint-prod.sh
COPY ./docker/python/entrypoint.sh $APP_HOME

# copy project
COPY ./app $APP_HOME

# chown all the files to the app user
RUN chown -R whitenet:whitenet $APP_HOME

# change to the app user
USER whitenet

# set entrypoint as executable
RUN chmod +x /home/whitenet/web/entrypoint.sh

# run entrypoint.prod.sh
ENTRYPOINT ["/home/whitenet/web/entrypoint.sh"]