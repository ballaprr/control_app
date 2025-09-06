from django.shortcuts import render
from .models import Device

# Create your views here.


# View to get device ids and put into TILE_DEVICE_MAP
def get_device_ids(request):
    devices = Device.objects.all()
    TILE_DEVICE_MAP = {}
    for device in devices:
        TILE_DEVICE_MAP[device.tile_label] = device.device_id
    return TILE_DEVICE_MAP

