FROM python:3.7-alpine as builder
MAINTAINER Makrushin Egor egormm@gmail.com

WORKDIR /usr/src/gonm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POSTGRESQL_CLIENT_V=12.2-r0 \
    POSTGRESQL_DEV_V=12.2-r0 \
    POSTGRESQL_DEV_V=12.2-r0 \
    MUSL_DEV_V=1.1.24-r2 \
    GCC_V=9.2.0-r4

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/v3.11/main \
        musl-dev=${MUSL_DEV_V} \
        gcc=${GCC_V} \
        postgresql-client=${POSTGRESQL_CLIENT_V} \
        postgresql-dev=${POSTGRESQL_DEV_V}


# install dependencies
RUN pip install --upgrade pip
COPY ./docker/python/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/gonm/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.7-alpine


# create directory for the app user
RUN mkdir -p /home/gonm

# create the app user
RUN addgroup -S gonm && adduser -S gonm -G gonm

# create the appropriate directories
ENV HOME=/home/gonm \
    APP_HOME=/home/gonm/web \
    MUSL_DEV_V=1.1.24-r2 \
    GCC_V=9.2.0-r4 \
    BASH_V=5.0.11-r1 \
    GRAPHVIZ_V=2.42.3-r0 \
    TTF_FREEFONT_V=20120503-r1 \
    CURL_V=7.67.0-r0 \
    GDAL_DEV_V=3.0.3-r0 \
    GEOS_DEV_V=3.8.0-r0 \
    PROJ_DEV_V=6.2.1-r0


RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install graphviz and geos dependencies

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/v3.11/main \
    musl-dev=${MUSL_DEV_V} \
    gcc=${GCC_V} \
    bash=${BASH_V} \
    graphviz=${GRAPHVIZ_V} \
    ttf-freefont=${TTF_FREEFONT_V} \
    curl=${CURL_V} \
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/v3.11/community \
                          --repository http://dl-cdn.alpinelinux.org/alpine/v3.11/main \
    gdal-dev=${GDAL_DEV_V} \
    geos-dev=${GEOS_DEV_V} \
    proj-dev=${PROJ_DEV_V}


# install dependencies
COPY --from=builder /usr/src/gonm/wheels /wheels
COPY --from=builder /usr/src/gonm/requirements.txt .
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache /wheels/*

# copy entrypointsh
COPY ./docker/python/entrypoint.sh $APP_HOME

# copy project
COPY ./app $APP_HOME

# chown all the files to the app user
RUN chown -R gonm:gonm $APP_HOME

# change to the app user
USER gonm

# make entrypoint executable
RUN chmod +x $APP_HOME/entrypoint.sh


# run entrypoint.prod.sh
ENTRYPOINT ["/home/gonm/web/entrypoint.sh"]