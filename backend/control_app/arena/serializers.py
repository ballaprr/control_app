from rest_framework import serializers
from .models import Arena
from user.serializers import UserSerializer


class ArenaSerializer(serializers.ModelSerializer):
    active_controller = UserSerializer(read_only=True)
    active_controller_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Arena
        fields = ('id', 'arena_name', 'brightness', 'active_controller', 'active_controller_id')

    def validate_arena_name(self, value):
        instance = getattr(self, 'instance', None)
        if Arena.objects.filter(arena_name=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Arena with this name already exists.")
        return value


class ArenaListSerializer(serializers.ModelSerializer):
    active_controller_username = serializers.CharField(source='active_controller.username', read_only=True)

    class Meta:
        model = Arena
        fields = ('id', 'arena_name', 'brightness', 'active_controller_username')
