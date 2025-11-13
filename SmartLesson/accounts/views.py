from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from django.urls import reverse

from django.contrib.auth.models import User

from .models import Profile, Notification

from .decorators import role_required

from .forms import SignUpForm, LoginForm, UserUpdateForm, ProfileUpdateForm

from lessonplans.models import LessonPlan

def ict_officer_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('accounts:login')
        if not hasattr(user, 'profile') or user.profile.user_role != 'ict_officer':
            messages.error(request, "Access denied: Only ICT Officers can manage users.")
            return redirect('core:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Create your views here.
@role_required('ict_officer')
@ict_officer_required
def manage_users(request):
    query = request.GET.get('q', '')  # Get search term from URL

    # Filter users if a search term is entered
    users = User.objects.all().order_by('-date_joined')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(profile__user_role__icontains=query)
        ).distinct()

    # Paginate results
    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/manage_users.html', {
        'page_obj': page_obj,
        'query': query,
    })

@role_required('teacher', 'admin', 'ict_officer')
def profile_view(request):
    user = request.user
    profile = user.profile  # assuming OneToOne relationship

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@role_required('ict_officer')
@ict_officer_required
def create_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        user_role = request.POST.get('user_role')
        if form.is_valid():
            if request.user.profile.user_role != 'admin' or request.user.profile.user_role != 'ict_officer' and user_role != 'teacher':
                messages.error(request, "Only admins can create a non-teacher account.")
                return redirect('accounts:signup')
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            
            return redirect('core:index')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {
        'form': form,
        })

@role_required('ict_officer')
@ict_officer_required
def edit_user(request, user_uuid):
    profile = get_object_or_404(Profile, uuid=user_uuid)
    user = profile.user

    if request.method == 'POST':
        form = SignUpForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Update existing profile instead of creating a new one
            profile.phone_number = form.cleaned_data.get('phone_number', profile.phone_number)
            profile.tsc_number = form.cleaned_data.get('tsc_number', profile.tsc_number)
            profile.id_number = form.cleaned_data.get('id_number', profile.id_number)
            profile.user_role = form.cleaned_data.get('user_role', profile.user_role)
            profile.save()

            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect('manage_users')
    else:
        # Pre-fill the form with both User and Profile data
        initial_data = {
            'phone_number': profile.phone_number,
            'tsc_number': profile.tsc_number,
            'id_number': profile.id_number,
            'user_role': profile.user_role,
            'email': user.email,
        }
        form = SignUpForm(instance=user, initial=initial_data)

    return render(request, 'accounts/signup.html', {
        'form': form,
        'is_edit': True,
        'user_obj': user,
        'profile': profile,
    })


def login_view(request, role=None):
    if role not in ['teacher', 'admin', 'ict_officer']:
        messages.error(request, "Invalid login type.")
        return redirect('core:index')

    role_titles = {
        'teacher': "Teacher Login",
        'admin': "Administrator Login",
        'ict_officer': "ICT Officer Login"
    }
    form_title = role_titles.get(role, "User Login")

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if user.profile.user_role != role:
                messages.error(request, f"You are not authorized to log in as a {role.replace('_', ' ')}.")
                return redirect(reverse(f"accounts:{role}_login"))

            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            return redirect('core:index')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'form_title': form_title,
    })

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:index')

@role_required('teacher', 'admin', 'ict_officer')
def notifications(request):
    notifications = request.user.notifications.all().order_by('created_at')

    return render(request, 'accounts/notifications.html', {'notifications': notifications})

@require_POST
@role_required('teacher', 'admin', 'ict_officer')
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])

    return redirect('accounts:notifications')

@role_required('teacher', 'admin', 'ict_officer')
def fetch_notifications(request):
    """Return unread notifications as JSON."""
    unread = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    data = [
        {
            "id": n.id,
            "message": n.message,
            "created_at": n.created_at.strftime("%b %d, %Y %H:%M"),
        }
        for n in unread
    ]
    return JsonResponse({"notifications": data})