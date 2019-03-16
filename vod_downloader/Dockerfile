FROM python:3.7.2-alpine3.9
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir /chatlogs && mkdir /app
COPY Twitch-Chat-Downloader/requirements.txt /tmp/requirements.txt
COPY . /app
RUN pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /app