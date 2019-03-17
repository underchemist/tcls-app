FROM python:3.7-alpine3.9
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir /chatlogs && mkdir /app
COPY Twitch-Chat-Downloader/requirements.txt /tmp/tcd-requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir -r /tmp/tcd-requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /app