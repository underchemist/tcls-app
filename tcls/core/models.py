from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.dateparse import parse_datetime

class Video(models.Model):
    data = JSONField(encoder=DjangoJSONEncoder)

    @classmethod
    def from_db(cls, db, field_names, values):
        new = super().from_db(db, field_names, values)
        new.data['created_at'] = parse_datetime(new.data['created_at'])
        new.data['published_at'] = parse_datetime(new.data['published_at'])

        return new


class LogFile(models.Model):
    filepath = models.FileField(max_length=200)
    video_id = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ChatComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    time = models.DurationField(blank=True)
    username = models.CharField(max_length=256, blank=True)
    msg = models.CharField(max_length=512)  # twich chat max char count is apparently 500
    logfile = models.ForeignKey(LogFile, on_delete=models.CASCADE)