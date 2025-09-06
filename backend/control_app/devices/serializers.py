from rest_framework import serializers
from .models import Device
from arena.serializers import ArenaListSerializer


class DeviceSerializer(serializers.ModelSerializer):
    arena = ArenaListSerializer(read_only=True)
    arena_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Device
        fields = ('id', 'name', 'device_id', 'arena', 'arena_id', 'tile_label', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_device_id(self, value):
        instance = getattr(self, 'instance', None)
        if Device.objects.filter(device_id=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Device with this ID already exists.")
        return value

    def validate(self, attrs):
        arena_id = attrs.get('arena_id')
        tile_label = attrs.get('tile_label')
        instance = getattr(self, 'instance', None)
        
        if arena_id and tile_label:
            existing_device = Device.objects.filter(
                arena_id=arena_id, 
                tile_label=tile_label
            ).exclude(pk=instance.pk if instance else None)
            
            if existing_device.exists():
                raise serializers.ValidationError("A device with this tile label already exists in this arena.")
        
        return attrs


class DeviceListSerializer(serializers.ModelSerializer):
    arena_name = serializers.CharField(source='arena.arena_name', read_only=True)

    class Meta:
        model = Device
        fields = ('id', 'name', 'device_id', 'arena_name', 'tile_label', 'created_at')
