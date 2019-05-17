FROM python:3.6-alpine

RUN apk update \
  && apk add --virtual build-deps gcc python3-dev musl-dev file-dev \
  && apk add curl 


COPY ./requirements /requirements
COPY ./entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

RUN pip install -r /requirements/local.txt

ENV LANG en_GB.UTF-8
ENV TEST_ES_SERVER=elasticsearch:9200

WORKDIR /app
ENTRYPOINT ["/entrypoint"]