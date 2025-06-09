from guest_user.decorators import allow_guest_user
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Quest, Challenge, Progress, Badge, UserProfile
from .forms import QuestForm
from django.utils import timezone
from .forms import BadgeForm


def quest_list(request):
    quests = Quest.objects.all().order_by('-created_at')
    return render(request, 'quests/quest_list.html', {'quests': quests})

@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    progresses = Progress.objects.filter(user=request.user, completed=True)
    badges = Badge.objects.filter(xp_required__lte=user_profile.xp)
    quests = Quest.objects.filter(challenges__progress__user=request.user).distinct()
    return render(request, 'quests/dashboard.html', {
        'user_profile': user_profile,
        'progresses': progresses,
        'badges': badges,
        'quests': quests,
        'show_badge_message': False,  # <--- Add this line
    })

@allow_guest_user
def quest_detail(request, quest_id):
    quest = get_object_or_404(Quest, id=quest_id)
    challenges = quest.challenges.order_by('order')
    user_progress = {p.challenge.id: p for p in Progress.objects.filter(user=request.user, challenge__in=challenges)}
    return render(request, 'quests/quest_detail.html', {
        'quest': quest,
        'challenges': challenges,
        'user_progress': user_progress,
        'show_badge_message': False,  # <--- Add this line
    })

@allow_guest_user
def complete_challenge(request):
    if request.method == 'POST':
        challenge_id = request.POST.get('challenge_id')
        note = request.POST.get('note', '')
        challenge = get_object_or_404(Challenge, id=challenge_id)
        progress, created = Progress.objects.get_or_create(user=request.user, challenge=challenge)
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.note = note
        progress.save()
        
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.xp += 10
        if user_profile.xp >= 100:
            user_profile.level += 1
            user_profile.xp = 0
        user_profile.save()
        
        return JsonResponse({'success': True, 'level': user_profile.level, 'xp': user_profile.xp})
    return JsonResponse({'success': False})

@login_required
def create_quest(request):
    if request.method == 'POST':
        form = QuestForm(request.POST, request.FILES)
        if form.is_valid():
            quest = form.save(commit=False)
            quest.creator = request.user
            quest.save()
            for i in range(1, 6):
                title = request.POST.get(f'challenge_title_{i}')
                desc = request.POST.get(f'challenge_desc_{i}')
                if title and desc:
                    Challenge.objects.create(quest=quest, title=title, description=desc, order=i)
            return redirect('quest_detail', quest_id=quest.id)
    else:
        form = QuestForm()
    
    return render(request, 'quests/create_quest.html', {
        'form': form,
        'show_badge_message': True,  # <-- Add this line
    })

def create_badge(request):
    if not request.user.is_staff:
        return redirect('dashboard')  # Only staff/admins can add badges
    if request.method == 'POST':
        form = BadgeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BadgeForm()
    return render(request, 'quests/create_badge.html', {'form': form})

def delete_quest(request, quest_id):
    if not request.user.is_staff:
        return redirect('dashboard')  # Only staff/admins can delete quests
    quest = get_object_or_404(Quest, id=quest_id)
    if request.method == 'POST':
        quest.delete()
        return redirect('dashboard')
    return render(request, 'quests/confirm_delete_quest.html', {'quest': quest})

def create_quest_view(request):
    return render(request, 'skillsquest/create_quest.html')
