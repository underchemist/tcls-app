FROM amancevice/pandas:0.24.1-alpine
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir /app && mkdir /data
COPY requirements.txt /app
COPY twitch-chat-spam-counter /app/twitch-chat-spam-counter/
WORKDIR /app
RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip3 install -r requirements.txt --no-cache-dir && \
    pip3 install twitch-chat-spam-counter/. && \
    apk --purge del .build-deps
COPY . /app