from django.contrib import admin
from .models import Announcement, Notification, Photo, Profile

admin.site.register(Profile)
admin.site.register(Announcement)
admin.site.register(Notification)
admin.site.register(Photo)
