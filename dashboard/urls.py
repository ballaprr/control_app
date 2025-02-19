from django.urls import include, path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('control-view/', views.control_view, name='control_view'),
    path('takecontrol/', views.takecontrol, name='takecontrol'),
]