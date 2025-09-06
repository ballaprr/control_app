from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

app_name = 'user_api'

urlpatterns = [
    # Authentication endpoints
    path('register/', api_views.UserRegistrationView.as_view(), name='register'),
    path('login/', api_views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', api_views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User profile endpoints
    path('profile/', api_views.UserProfileView.as_view(), name='profile'),
    path('change-password/', api_views.ChangePasswordView.as_view(), name='change-password'),
    
    # Password reset endpoints
    path('forgot-password/', api_views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:uidb64>/<str:token>/', api_views.reset_password, name='reset-password'),
    
    # Email verification endpoints
    path('verify-email/<str:uidb64>/<str:token>/', api_views.verify_email, name='verify-email'),
    path('host-verify/<str:uidb64>/<str:token>/', api_views.host_verify, name='host-verify'),
]
