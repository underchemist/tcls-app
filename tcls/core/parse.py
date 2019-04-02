from django.utils.dateparse import parse_duration

from .models import LogFile

def parse_chatlog(lid):
    logfile = LogFile.objects.get(id=lid)

    with logfile.filepath.open('r') as f:
        data = f.readlines()

    for idx, line in enumerate(data):
        line_split = line.split(',')
        data[idx] = [parse_duration(line_split[0].strip('[]')), line_split[1], line_split[2].strip('\n')]

    return data
