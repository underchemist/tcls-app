from pathlib import Path
import os
import itertools
import functools

import twitch
from twitch import TwitchHelix
import celery
from celery import shared_task

from . import tasks
from .models import Video, LogFile, ChatComment

CLIENT_ID = os.getenv('TWITCH_API_CLIENT_ID')
OWL_USER_ID = '137512364'

class Channel:

    def __init__(self, user_id):
        self.user_id = user_id
        self.data_path = Path('/chatlogs')
        self.client = TwitchHelix(client_id=CLIENT_ID)
        self.vods = Vods()

    def _get_all_archived_vods(self):
        video_iter = self.client.get_videos(
            user_id=self.user_id,
            page_size=100,
            video_type='archive'
        )

        all_vods = Vods()

        for video_page in video_iter:
            all_vods.append(video_page)

        return all_vods

    def _get_vods_by_id(self, ids):
        video_iter = self.client.get_videos(
            video_ids=ids,
            page_size=100
        )

        all_vods = Vods()

        for video_page in video_iter:
            all_vods.append(video_page)

        return all_vods

    def get_vods(self):
        self.vods = self._get_all_archived_vods()

    def get_vods_by_id(self, ids):
        self.vods = self._get_vods_by_id(ids)


class Vods(list):

    def to_list_of_dict(self):
        return [dict(v) for v in self]


def newest(a, b):
    # relies on duration string being compared properly
    if a['duration'] < b['duration']:
        return b
    elif a['duration'] > b['duration']:
        return a

    # if identical in duration then will remove
    return None

def diff(old, new):
    intersect = [item for item in old if item in new]
    sym_diff = [item for item in itertools.chain(old, new) if item not in intersect]
    key_func = lambda x: x['id']
    sym_diff_sorted = sorted(sym_diff, key=key_func)
    g = itertools.groupby(sym_diff_sorted, key=key_func)
    d = dict()

    for k, v in g:
        d[k] = functools.reduce(newest, list(v))

    # strip None values where two vods where different but had same duration
    return [i for i in list(d.values()) if i is not None]

def compare_db_vods_to_new():
    qs = Video.objects.all()
    vods_db = [v.data for v in qs]

    owl = Channel(OWL_USER_ID)
    owl.get_vods()
    vods_api = owl.vods.to_list_of_dict()

    return diff(vods_db, vods_api)

def compare_db_vods_to_log():
    return Video.objects.filter(logfile__pk__isnull=True)

def add_videos(vod_list):
    """Add Video objects to db.

    Args:
        vod_list (list of dict): List of twitch vod objects to add.
    """
    for data in vod_list:
        Video.objects.update_or_create(data=data)

def get_chat_chain(vid):
    """Execute worker to get chatlog from twitch api

    Arguments:
        vid (int): pk of Video object.
    """
    video = Video.objects.get(pk=vid)
    t = tasks.get_remote_sig(
        'vod_downloader.download_chat_by_id',
        args=[video.data['id']]
        )

    c = celery.chain(
        t,
        tasks.create_logfile.s(video.data['user_name'].lower(), vid)
        )

    return c

def get_all_chat_from_qs(qs=None):
    if qs is None:
        qs = compare_db_vods_to_log()
    task_list = []
    for video in qs:
        task_list.append(get_chat_chain(video.id))

    g = celery.group(task_list)
    g.apply_async()

def load_chatcomment_from_logfile(qs=None):
    if qs is None:
        qs = LogFile.objects.has_no_chatcomment()

    task_list = []
    for logfile in qs:
        task_list.append(tasks.create_chatcomments.s(logfile.id))

    g = celery.group(task_list)
    group_result = g.apply_async()

    return group_result
