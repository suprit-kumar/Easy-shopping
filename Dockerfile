FROM python:3.8.3-alpine

ENV MICRO_SERVICE=/home/app/microservice
ARG APP_USER="demo-user"
ARG APP_GROUP="demo-user"
RUN addgroup -S $APP_USER && adduser -S $APP_USER -G $APP_USER
# set work directory


RUN mkdir -p $MICRO_SERVICE
RUN mkdir -p $MICRO_SERVICE/static

# where the code lives
WORKDIR $MICRO_SERVICE

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk add jpeg-dev zlib-dev libjpeg \
    && apk del build-deps \
    && apk --no-cache add musl-dev linux-headers g++
# install dependencies
RUN pip install --upgrade pip
# copy project
COPY ${PWD}/greatkart/postgre_requirements.txt /$MICRO_SERVICE/postgre_requirements.txt
RUN pip install -r postgre_requirements.txt
COPY ${PWD}/greatkart /$MICRO_SERVICE

CMD ["/bin/bash", "/home/app/microservice/entrypoint.sh"]