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
        user = User.objects.filter(email=email).first()
        if user:
            messages.error(request, 'Email already exists')
        else:
            user = User.objects.create_user(email=email, password=password)
            login(request, user)
            return redirect('arena:select_arena')

    return render(request, 'user/register.html')

# check