"""control_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.control_view, name='control_view'),
    path('trigger-action/', views.trigger_action, name='trigger_action'),
    path('device-output/<int:title_Index>/', views.device_output, name='device_output'),
    path('blackscreen/', views.blackscreen, name='blackscreen'),
    path('get-deviceid/<int:tileIndex>/', views.get_deviceid, name='get_deviceid'),
    path('reboot-device/', views.reboot_device, name='reboot_device'),
    path('fetch-legend-data/<int:setup_id>/', views.fetch_legend_data_api, name='fetch_legend_data'),
    path('page_1/', views.my_page, name='my_page'),
]
