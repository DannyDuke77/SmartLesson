from django.shortcuts import render
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.contrib import messages

from .forms import SignUpForm, LoginForm

# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        user_role = request.POST.get('user_role')
        if form.is_valid():
            if user_role != 'teacher':
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