from django.urls import path
from . import views

urlpatterns = [
    path('trigger-action/', views.trigger_action, name='trigger_action'),
    path('get-tiles/', views.get_device_output, name='get_device_output'),
]