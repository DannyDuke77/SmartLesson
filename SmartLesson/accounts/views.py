from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q

from django.contrib.auth.models import User

from .models import Profile

from .forms import SignUpForm, LoginForm

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
@login_required
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


@login_required
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

@login_required
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


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Accept returning to ?next= parameter if present
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            return redirect('core:index')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:index')