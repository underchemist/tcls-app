import json

from django.contrib import admin

from .models import LogFile, ChatComment, Video

class VideoAdmin(admin.ModelAdmin):
    fields = ('data_readonly',)
    readonly_fields = ('data_readonly', )

    def data_readonly(self, instance):
        response = json.dumps(instance.data, default=str)

        return response
admin.site.register(LogFile)
admin.site.register(ChatComment)
admin.site.register(Video, VideoAdmin)