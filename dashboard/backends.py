from django.contrib.auth.backends import BaseBackend
from .models import Arena

class ArenaAuthenticationBackend(BaseBackend):
    def authenticate(self, request, arena_name=None):
        try:
            return Arena.objects.get(arena_name=arena_name)
        except Arena.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Arena.objects.get(pk=user_id)
        except Arena.DoesNotExist:
            return None
