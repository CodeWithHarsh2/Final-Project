from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    xp = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)    
    friends = models.ManyToManyField('self', blank=True)
    
    
    def __str__(self):
        return self.user.username

class Quest(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quests')
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='quest_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Challenge(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='challenges')
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quest.title}: {self.title}"

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    photo = models.ImageField(upload_to='progress_photos/', blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'challenge')

class Badge(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/', null=True, blank=True)
    icon_url = models.URLField(blank=True, null=True)  # <-- Add this line
    xp_required = models.IntegerField(default=0)


    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from .models import UserProfile
        UserProfile.objects.create(user=instance)

class Competition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    participants = models.ManyToManyField(UserProfile, through='CompetitionEntry')
    reward_xp = models.IntegerField(default=100)
    badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)

class CompetitionEntry(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
