from celery import shared_task
from . import twitch
from .models import Video

@shared_task
def hello():
    print('Hello there!')

@shared_task
def load_owl_videos():
    qs = Video.objects.all()
    qs.delete()

    owl_channel = twitch.Channel(twitch.OWL_USER_ID)
    owl_channel.get_vods()

    Video.objects.bulk_create(
        [Video(data=v) for v in owl_channel.vods.to_list_of_dict()]
    )