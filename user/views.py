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


# Need to enhance by signing up and send email to admin to approve
# User gets email back saying they're approved and can continue
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


def change_password_step1_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            request.session['email'] = email
            return redirect('user:change_password_step2_view')
        else:
            messages.error(request, 'Email does not exist')
    return render(request, 'user/change_password_step1.html')

def change_password_step2_view(request):
    email = request.session.get('email')
    if not email:
        return redirect('user:change_password_step1')

    if request.method == 'POST':
        old_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        user = User.objects.filter(email=email).first()
        print(user)
        if user and user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password changed successfully')
            return redirect('user:login_view')
        else:
            messages.error(request, 'Old password is incorrect')

    return render(request, 'user/change_password_step2.html')
