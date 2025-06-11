from guest_user.decorators import allow_guest_user
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .models import Quest, Challenge, Progress, Badge, UserProfile, CompetitionEntry, Competition
from .forms import QuestForm
from django.utils import timezone
from .forms import BadgeForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserProfile, Progress, Badge, Quest
from django.views.decorators.csrf import csrf_exempt
from .forms import UserProfileForm
from .forms import CompetitionForm




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

    # Check for the instructions popup session variable (for SweetAlert2 or similar)
    show_instructions = request.session.pop('show_instructions', False)
    print("show_instructions:", show_instructions)
    return render(request, 'quests/dashboard.html', {
        'user_profile': user_profile,
        'progresses': progresses,
        'badges': badges,
        'quests': quests,
        'show_badge_message': show_badge_message,
        'xp_percent': xp_percent,
        'show_instructions': show_instructions,  # <-- for the popup
        
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
def leaderboard(request):
    # Top 10 users by XP
    users = UserProfile.objects.order_by('-xp')[:10]
    return render(request, 'quests/leaderboard.html', {'users': users})

@allow_guest_user
def complete_challenge(request, challenge_id):
    if request.method == 'POST':
        challenge = get_object_or_404(Challenge, id=challenge_id)
        progress, created = Progress.objects.get_or_create(user=request.user, challenge=challenge)
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.save()

        user_profile = UserProfile.objects.get(user=request.user)
        xp_before = user_profile.xp + 10  # Calculate XP before reset
        xp_percent = xp_before if xp_before <= 100 else 100  # Always cap at 100 for popup

        if xp_before >= 100:
            user_profile.level += 1
            user_profile.xp = 0
        else:
            user_profile.xp = xp_before
        user_profile.save()

        # ======== NEW COMPETITION CODE start_datetime ========
        # Update competition scores for active competitions
        active_entries = CompetitionEntry.objects.filter(
            user=user_profile,
            competition__start_datetime__lte=timezone.now(),
            competition__end_datetime__gte=timezone.now()
        )
        for entry in active_entries:
            entry.score += 10  # Award 10 points per challenge completion
            entry.save()
        # ======== NEW COMPETITION CODE END ========

        return JsonResponse({
            'success': True,
            'level': user_profile.level,
            'xp': user_profile.xp,
            'xp_percent': xp_percent  # Pass pre-reset XP for popup check
        })
    
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
    if request.user.username != "Harsh":
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

    
def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['show_instructions'] = True  # THIS LINE IS CRUCIAL
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})

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

@login_required
def competition_list(request):
    user_profile = UserProfile.objects.get(user=request.user)
    competitions = Competition.objects.filter(end_datetime__gte=timezone.now())
    joined_ids = CompetitionEntry.objects.filter(user=user_profile).values_list('competition_id', flat=True)
    return render(request, 'quests/competition_list.html', {
        'competitions': competitions,
        'joined_ids': set(joined_ids),
        'user_profile': user_profile,
    })

@login_required
def join_competition(request, competition_id):
    if request.method == 'POST':
        competition = get_object_or_404(Competition, id=competition_id)
        user_profile = UserProfile.objects.get(user=request.user)
        CompetitionEntry.objects.get_or_create(user=user_profile, competition=competition)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})





@login_required
def competition_detail(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    entries = CompetitionEntry.objects.filter(competition=competition).order_by('-score')
    user_entry = entries.filter(user__user=request.user).first()
    
    return render(request, 'quests/competition_detail.html', {
        'competition': competition,
        'entries': entries,
        'user_entry': user_entry
    })


def check_competition_winner(request):
    if not request.user.is_authenticated:
        return
    user_profile = UserProfile.objects.get(user=request.user)
    now = timezone.now()
    ended_comps = Competition.objects.filter(end_datetime__lt=now)
    for comp in ended_comps:
        top_score = CompetitionEntry.objects.filter(competition=comp).order_by('-score').first()
        if not top_score:
            continue
        winners = CompetitionEntry.objects.filter(competition=comp, score=top_score.score)
        if winners.filter(user=user_profile).exists():
            shown = request.session.get('competition_win_shown', [])
            if comp.id not in shown:
                request.session['show_competition_win'] = comp.id
                shown.append(comp.id)
                request.session['competition_win_shown'] = shown


@login_required
def profile(request, username=None):
    if username:
        user_profile = get_object_or_404(UserProfile, user__username=username)
        is_owner = (request.user.username == username)
    else:
        user_profile = UserProfile.objects.get(user=request.user)
        is_owner = True

    edit_mode = is_owner and request.GET.get("edit") == "1"

    if request.method == 'POST' and is_owner:
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            # Redirect to profile view mode after saving
            return redirect('profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'users/profile.html', {
        'profile_user': user_profile.user,
        'user_profile': user_profile,
        'form': form,
        'is_owner': is_owner,
        'edit_mode': edit_mode,
    })



@csrf_exempt
def clear_competition_win(request):
    if request.method == 'POST':
        request.session.pop('show_competition_win', None)
        return JsonResponse({'cleared': True})
    return JsonResponse({'cleared': False})

def create_competition(request):
    if request.method == "POST":
        form = CompetitionForm(request.POST)
        if form.is_valid():
            form.save()
            # redirect or show success
    else:
        form = CompetitionForm()
    return render(request, "competitions/competition_form.html", {"form": form})