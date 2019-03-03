from core.models import LogFile, ChatComment
from pathlib import Path
from django.utils.dateparse import parse_duration
from itertools import islice
from django import db

def from_json(path):
    """Load rechattool processed output into memory

    Arguments:
        path {pathlib.Path} -- Path to processed chatlog.
    """
    with path.open(mode='r', encoding='utf-8-sig') as f:
        chatlog = f.readlines()

    strip = lambda x:x.strip('[]:\n ')

    chatlog_split = [line.split(' ', maxsplit=2) for line in chatlog]

    chatlog_stripped = [list(map(strip, line)) for line in chatlog_split]

    chatlog_parsed = [[parse_duration(time), user, msg] for time, user, msg in chatlog_stripped]

    return chatlog_parsed

def parse_id_logfile(filename):
    return filename.name.split('id')[1].split('_', maxsplit=1)[0]

def write_chatlog_to_db(chatlog, filename, batch_size=500):
    video_id = parse_id_logfile(filename)
    l = LogFile(raw_data=str(filename), video_id=video_id)
    l.save()

    objs = (ChatComment(
            time=line[0],
            username=line[1],
            msg=line[2],
            logfile=l
        ) for line in chatlog)

    ChatComment.objects.bulk_create(objs, batch_size)
    db.reset_queries()

def get_all_chatlog_filenames(path):
    p = Path(path)

    return sorted(p.glob('*.txt'))

def run():
    chatlog_filenames = get_all_chatlog_filenames('/chatlogs')

    for f in chatlog_filenames:
        chatlog = from_json(f)
        write_chatlog_to_db(chatlog, f)
