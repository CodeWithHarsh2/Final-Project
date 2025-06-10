from guest_user.decorators import allow_guest_user
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .models import Quest, Challenge, Progress, Badge, UserProfile
from .forms import QuestForm
from django.utils import timezone
from .forms import BadgeForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages




def quest_list(request):
    quests = Quest.objects.all().order_by('-created_at')
    return render(request, 'quests/quest_list.html', {'quests': quests})



@login_required
def dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    progresses = Progress.objects.filter(user=request.user, completed=True)
    badges = Badge.objects.filter(xp_required__lte=user_profile.xp)
    quests = Quest.objects.filter(challenges__progress__user=request.user).distinct()
    
    # XP percent for progress bar (assumes 100 XP per level)
    xp_percent = int((user_profile.xp / 100) * 100) if user_profile.xp <= 100 else 100

    # Show badge message if no badges
    show_badge_message = not badges.exists()

    return render(request, 'quests/dashboard.html', {
        'user_profile': user_profile,
        'progresses': progresses,
        'badges': badges,
        'quests': quests,
        'show_badge_message': show_badge_message,
        'xp_percent': xp_percent,
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
def complete_challenge(request, challenge_id):
    if request.method == 'POST':
        # Use challenge_id from the URL, not from POST data
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


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")  # Note: `password1` from UserCreationForm
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Account created successfully! You are now logged in.")
                return redirect('dashboard')
            else:
                messages.error(request, "Authentication failed.")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def create_quest(request):
    if request.user.username != "harsh":
        return render(request, 'quests/access_denied.html')
    
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
        'show_badge_message': True,
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
