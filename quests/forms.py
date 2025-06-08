from django import forms
from .models import Quest
from .models import Badge

class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ['title', 'description', 'image']

class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = ['name', 'description', 'icon', 'xp_required']
