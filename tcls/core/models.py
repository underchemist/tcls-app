from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.dateparse import parse_datetime, parse_duration
from datetime import timedelta

class Video(models.Model):
    data = JSONField(encoder=DjangoJSONEncoder)
    archived = models.BooleanField(default=False)

    @classmethod
    def from_db(cls, db, field_names, values):
        new = super().from_db(db, field_names, values)
        new.data['created_at'] = parse_datetime(new.data['created_at'])
        new.data['published_at'] = parse_datetime(new.data['published_at'])

        return new

    def __str__(self):
        return self.data['title']

class LogFileManager(models.Manager):

    def has_no_chatcomment(self):
        qs = LogFile.objects.filter(chatcomment__isnull=True)

        return qs

class LogFile(models.Model):
    video = models.OneToOneField(Video, on_delete=models.CASCADE)
    filepath = models.FileField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = LogFileManager()

    def _tail(self, offset=-1024):
        """Determine the approximate duration of the chatlog by tailing the end of the logfile """
        with self.filepath.open('rb') as f:
            f.seek(offset, 2)  # seek to almost EOF
            tail = [line.decode('utf-8', 'ignore') for line in f.readlines()]

            return tail

    def _calc_duration(self):
        tail = self._tail()

        duration_str = tail[-1].split(',')[0].strip('[]')
        duration = parse_duration(duration_str)

        return duration

    def _is_similar_duration(self,tol=timedelta(minutes=1)):
        """Compare calculated duration of chatlog and the duration from video object in order to say whether the chatlog has actually downloaded the full amount
        """
        chatlog_duration = self._calc_duration()
        video_duration = parse_duration(self.video.data['duration'].replace('m', ':').replace('h', ':').strip('s'))

        return video_duration - chatlog_duration < tol

class ChatComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    time = models.DurationField(blank=True)
    username = models.CharField(max_length=256, blank=True)
    msg = models.CharField(max_length=512)  # twich chat max char count is apparently 500
    logfile = models.ForeignKey(LogFile, on_delete=models.CASCADE)