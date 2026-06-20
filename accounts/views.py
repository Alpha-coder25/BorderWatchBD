from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from django.utils import timezone
from .forms import UserRegisterForm, ProfileUpdateForm
from .models import AnonymousToken

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created for {user.username}! You can now login.")
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {username}!")
                return redirect('core:home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('core:home')

@login_required
def profile_view(request):
    from .models import Profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=profile)
        
    user_reports = request.user.reports.all().order_by('-created_at')
    
    context = {
        'form': form,
        'reports': user_reports,
        'profile': profile
    }
    return render(request, 'accounts/profile.html', context)

def generate_anonymous_token_view(request):
    """
    Generate an anonymous token and display it to the user.
    """
    token_obj = None
    if request.method == 'POST':
        # Create a new token
        token_obj = AnonymousToken.objects.create()
        messages.success(request, "A new anonymous token has been generated successfully.")
    
    # Show active tokens if requested or just the newly generated one
    context = {
        'token_obj': token_obj,
    }
    return render(request, 'accounts/anonymous_token.html', context)
