from django.contrib import admin
from .models import UserProfile, Quest, Challenge, Progress, Badge

admin.site.register(UserProfile)
admin.site.register(Quest)
admin.site.register(Challenge)
admin.site.register(Progress)
admin.site.register(Badge)
