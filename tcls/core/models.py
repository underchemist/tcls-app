from django.db import models

class LogFile(models.Model):
    raw_data = models.FileField(max_length=200)
    video_id = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ChatComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    time = models.DurationField(blank=True)
    username = models.CharField(max_length=256, blank=True)
    msg = models.CharField(max_length=512)  # twich chat max char count is apparently 500
    logfile = models.ForeignKey(LogFile, on_delete=models.CASCADE)