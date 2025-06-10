from django.contrib import admin
from .models import UserProfile, Quest, Challenge, Progress, Badge, Competition,CompetitionEntry

admin.site.register(UserProfile)
admin.site.register(Quest)
admin.site.register(Challenge)
admin.site.register(Progress)
admin.site.register(Badge)

class CompetitionEntryInline(admin.TabularInline):
    model = CompetitionEntry
    extra = 0

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date')
    inlines = [CompetitionEntryInline]