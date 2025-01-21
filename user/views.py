from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User
from arena.models import Arena


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('arena:select_arena')
        else:
            messages.error(request, 'Email or password is incorrect')

    return render(request, 'user/login.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')
        user = User.objects.filter(email=email).first()
        if user:
            messages.error(request, 'Email already exists')
        else:
            user = User.objects.create_user(email=email, password=password, username=username)
            user = authenticate(request, email=email, password=password)
            login(request, user)
            return redirect('arena:select_arena')

    return render(request, 'user/register.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            messages.success(request, 'Password reset link sent to your email')
        else:
            messages.error(request, 'Email does not exist')
    return render(request, 'user/forgot_password.html')

def change_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(password)
            user.save()
            messages.success(request, 'Password changed successfully')
        else:
            messages.error(request, 'Email does not exist')
    return render(request, 'user/change_password.html')
