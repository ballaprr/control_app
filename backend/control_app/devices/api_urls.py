from django.urls import path
from . import api_views

app_name = 'devices_api'

urlpatterns = [
    # Device CRUD endpoints
    path('', api_views.DeviceListCreateView.as_view(), name='device-list-create'),
    path('<int:pk>/', api_views.DeviceDetailView.as_view(), name='device-detail'),
    
    # Device-specific endpoints
    path('arena/<int:arena_id>/', api_views.devices_by_arena, name='devices-by-arena'),
    path('reboot/', api_views.reboot_device, name='reboot-device'),
    path('action/', api_views.trigger_device_action, name='trigger-action'),
]
