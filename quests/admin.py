from django.contrib import admin
from .models import UserProfile, Quest, Challenge, Progress, Badge, Competition, CompetitionEntry
from django.contrib.admin.widgets import AdminSplitDateTime
from django import forms

# Register models with default admin
admin.site.register(Quest)
admin.site.register(Challenge)
admin.site.register(Progress)
admin.site.register(Badge)

# Custom admin for UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')

class CompetitionAdminForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = "__all__"
        widgets = {
            'start_datetime': AdminSplitDateTime(),
            'end_datetime': AdminSplitDateTime(),
        }

class CompetitionAdmin(admin.ModelAdmin):
    form = CompetitionAdminForm
    list_display = ('title', 'start_datetime', 'end_datetime')
    
admin.site.register(Competition, CompetitionAdmin)
