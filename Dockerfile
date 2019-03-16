FROM amancevice/pandas:0.24.1-alpine
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir /app && mkdir /chatlogs && mkdir /vendor
COPY requirements.txt /tmp/requirements.txt
COPY vendor/twitch-chat-spam-counter /tmp/twitch-chat-spam-counter
RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    pip3 install /tmp/twitch-chat-spam-counter/. && \
    apk --purge del .build-deps
WORKDIR /app