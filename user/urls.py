from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register_view, name='register_view'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password_view'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password_view'),
    path('change-password-step1/', views.change_password_step1_view, name='change_password_step1_view'),
    path('change-password-step2/', views.change_password_step2_view, name='change_password_step2_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
]
