from pathlib import Path
import os
import logging

from celery import shared_task, signature

from . import twitch, parse
from .models import Video, LogFile, ChatComment

logger = logging.getLogger(__name__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logger.setLevel(level=LOGLEVEL)

def get_remote_sig(remote_name, *args, **kwargs):
    return signature(remote_name, queue='vod_queue', *args, **kwargs)

@shared_task
def create_logfile(filename, username, vid):
    """Create instance of LogFile

    Should be used in chained task with remote download_chat_by_id task

    Args:
        filename (str): Filename of downloaded chat log.
        username (str): Username of twitch channel. Required to find the file
            as Twitch-Chat-Downloader saves output to
            /chatlogs/<username>/<filename>.
        vid (int or str): Id of tcls video object.
    """
    if filename is None:
        logger.info('Chat comments did not successfully download, not creating LogFile')
        return None

    filepath = Path('/chatlogs', username, filename)
    try:
        video = Video.objects.get(id=vid)
        obj, created = LogFile.objects.update_or_create(filepath=str(filepath), video=video)
        if created:
            logger.info('Created LogFile {} with file: {}'.format(obj.id, obj.filepath.name))
        else:
            logger.info('Updated LogFile {} with file: {}'.format(obj.id, obj.filepath.name))
        video.logfile = obj
        video.save()
    except LogFile.MultipleObjectsReturned as e:
        logger.error('There are multiple LogFile objects with same fields', exc_info=e)

@shared_task
def create_chatcomments(lid):
    chat = parse.parse_chatlog(lid)
    logfile = LogFile.objects.get(id=lid)

    chat_comments = [ChatComment(time=line[0], username=line[1], msg=line[2], logfile=logfile) for line in chat]

    ChatComment.objects.bulk_create(chat_comments)

@shared_task
def get_twitch_vods_daily():
    logger.info('Starting daily vod fetch task')
    new_vods = twitch.get_new_vods()

    if new_vods:
        logger.info('Found {} new vods from twitch: {}'.format(len(new_vods), ', '.join([v['title'] for v in new_vods])))
        twitch.add_videos(new_vods)
        logger.info('Adding vods to db')

        # get queryset of Video that don't have corresponding logfile
        video_qs = twitch.compare_db_vods_to_log()

        getchat_result = twitch.get_all_chat_from_qs(video_qs)
        getchat_result.get()

        load_chatcomment_result = twitch.load_chatcomment_from_logfile()
        load_chatcomment_result.get()