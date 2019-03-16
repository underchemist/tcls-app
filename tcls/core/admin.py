from django.contrib import admin

from .models import LogFile, ChatComment, Video

admin.site.register(LogFile)
admin.site.register(ChatComment)
admin.site.register(Video)