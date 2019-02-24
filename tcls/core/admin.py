from django.contrib import admin

from .models import LogFile, ChatComment

admin.site.register(LogFile)
admin.site.register(ChatComment)