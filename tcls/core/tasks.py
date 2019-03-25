from pathlib import Path
import os
import logging

from celery import shared_task, signature

from . import twitch
from .models import Video, LogFile

logger = logging.getLogger(__name__)
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logger.setLevel(level=LOGLEVEL)

def get_remote_sig(remote_name, *args, **kwargs):
    return signature(remote_name, queue='vod_queue', *args, **kwargs)

@shared_task
def reset_and_get_videos():
    qs = Video.objects.all()
    deleted = qs.delete()

    logging.debug('Deleted {} Video objects: {}'.format(len(deleted), deleted))

    owl_channel = twitch.Channel(twitch.OWL_USER_ID)
    owl_channel.get_vods()

    Video.objects.bulk_create(
        [Video(data=v) for v in owl_channel.vods.to_list_of_dict()]
    )

    logging.info('Added all archived videos from owl channel')

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
    except LogFile.MultipleObjectsReturned as e:
        logger.error('There are multiple LogFile objects with same fields', exc_info=e)