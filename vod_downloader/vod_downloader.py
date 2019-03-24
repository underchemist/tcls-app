import subprocess
import os
from pathlib import Path
import logging

from celery import Celery

logger = logging.getLogger(__name__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logger.setLevel(level=LOGLEVEL)

app = Celery('vod_downloader')

app.conf.update(
    accept_content=['application/json'],
    broker_url='redis://redis:6379',
    result_backend='redis://redis:6379',
    task_serializer='json',
    result_serializer='json'
)

TCD_BASE_DIR = '/app/Twitch-Chat-Downloader'

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task()
def download_chat_by_id(video_id):
    cmd_list = ['python', 'app.py', '--video', str(video_id), '--quiet', '-o', '/chatlogs', '--format', 'tcls']
    try:
        logger.info('Downloading chat comments for video {}'.format(video_id))
        result = subprocess.Popen(cmd_list, cwd=TCD_BASE_DIR)
        output = result.communicate()
        if output[1]:
            logger.error('Could not download chat comments for video {}: {}'.format(video_id, output[1]))
            return None
        logger.info('Downloaded chat comments for video {}. Output: {}, Error: {}'.format(video_id, output[0], output[1]))
        return 'v' + str(video_id) + '.txt'
    except Exception as e:
        logger.error('Something went wrong downloading chat comments for video {}'.format(video_id), exc_info=e)