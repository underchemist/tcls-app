from django.db import models

class LogFile(models.Model):
    raw_data = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ChatComment(models.Model):
    time = models.DateTimeField(blank=True)
    username = models.CharField(max_length=256, blank=True)
    msg = models.CharField(max_length=512)  # twich chat max char count is apparently 500
    logfile = models.ForeignKey(LogFile, on_delete=models.CASCADE)