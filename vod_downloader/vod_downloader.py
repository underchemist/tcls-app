from celery import Celery
import os
import subprocess

app = Celery('vod_downloader')

app.conf.update(
    accept_content=['application/json'],
    broker_url='redis://redis:6379',
    result_backend='redis://redis:6379',
    task_serializer='json',
    result_serializer='json'
)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task()
def download_vod(video_id):
    os.chdir('Twitch-Chat-Downloader')
    cmd_list = ['python', 'app.py', '--video', video_id, '--quiet', '-o', '/chatlogs']
    try:
        result = subprocess.Popen(cmd_list)
        result.wait()
    except Exception as e:
        print(e)