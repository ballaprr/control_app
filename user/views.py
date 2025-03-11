from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User
from arena.models import Arena
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def login_view(request):
    if request.user.is_authenticated:
        return redirect('arena:select_arena')  # Redirect logged-in users

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            if user.email_verified and user.admin_verified:
                login(request, user)
                request.session['user_id'] = user.id  # Set session token
                request.session['email'] = user.email
                return redirect('arena:select_arena')
            elif not user.email_verified:
                messages.error(request, 'Please verify your email before logging in')
            elif not user.admin_verified:
                messages.error(request, 'Your account is pending administrator approval')
        else:
            messages.error(request, 'Email or password is incorrect')

    return render(request, 'user/login.html')

def home_redirect_view(request):
    if request.user.is_authenticated:
        arenas = Arena.objects.all()
        return render(request, 'arena/select_arena.html', {'arenas': arenas})
    return render(request, 'user/login.html')

def logout_view(request):
    print("Check if logout is called")
    logout(request)
    request.session.flush()  # Clear session data
    messages.success(request, 'You have been logged out successfully')
    return redirect('user:login_view')

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
            user.email_verified = False
            user.save()
            
            # Generate verification token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse('user:verify_email', kwargs={'uidb64': uid, 'token': token})
            )
            message = f"Welcome to our platform! Please click the link below to verify your email:\n{verification_link}"
            
            send_mail(
                subject="Verify Your Email",
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('user:login_view')

    return render(request, 'user/register.html')

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Generate host verification token
        host_token = default_token_generator.make_token(user)
        host_verification_link = request.build_absolute_uri(
            reverse('user:host_verify', kwargs={'uidb64': uidb64, 'token': host_token})
        )
        
        # Send email to host for final verification
        host_message = f"""A new user has requested verification:
        
Email: {user.email}
Username: {user.username}

Please click the link below to approve or deny this verification:
{host_verification_link}"""

        send_mail(
            subject="User Verification Request",
            message=host_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to host email
            fail_silently=False,
        )
        messages.success(request, 'Your email verification request has been sent to the administrator for approval.')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
    
    return redirect('user:login_view')

def host_verify(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            verification_choice = request.POST.get('verification_choice')
            if verification_choice == 'approve':
                user.email_verified = True
                user.admin_verified = True
                user.save()
                # Send approval email to user
                send_mail(
                    subject="Account Verified",
                    message="Your account has been verified. You can now login to your account.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(request, 'User has been verified successfully.')
            else:
                # Send rejection email to user
                send_mail(
                    subject="Account Verification Denied",
                    message="Your account verification request has been denied. Please contact support for more information.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.error(request, 'User verification has been denied.')
            return redirect('user:login_view')
        return render(request, 'user/host_verify.html', {'uidb64': uidb64, 'token': token, 'user_email': user.email})
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('user:login_view')

def reset_password_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successfully')
                return redirect('user:login_view')
            else:
                messages.error(request, 'Passwords do not match')
        return render(request, 'user/reset_password.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'The reset link is invalid')
        return redirect('user:forgot_password_view')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(reverse('user:reset_password_view', kwargs={'uidb64': uid, 'token': token}))
            message = f"Click the link below to reset your password:\n{reset_link}"
            send_mail(
                subject="Password Reset Request",
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
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
        if user and user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password changed successfully')
            return redirect('user:login_view')
        else:
            messages.error(request, 'Old password is incorrect')

    return render(request, 'user/change_password_step2.html')
