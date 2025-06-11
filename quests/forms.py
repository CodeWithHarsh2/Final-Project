from django import forms
from .models import Quest
from .models import Badge, UserProfile, Competition
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ['title', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'style': 'resize:none;'}),
        }

class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = ['name', 'description', 'icon', 'xp_required']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'bio', 'description', 'birthday', 'age', 'residence',
            'address','email', 'phone', 'skype', 'freelance', 'quests_completed',
            'xp_collected', 'competitions_won', 'competitions_participated'
        ]
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'email': forms.Textarea(attrs={'rows': 1}),
        }



class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['title', 'description', 'start_datetime', 'end_datetime']  # Include description
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }







