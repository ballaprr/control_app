from django.contrib.auth.backends import BaseBackend
from arena.models import Arena

class ArenaAuthenticationBackend(BaseBackend):
    def authenticate(self, request, arena_name=None):
        if request is None:
            return None
        
        # Extract the arena_id from the request.session
        arena_id = request.session.get('arena_id')
        if arena_id:
            try:
                print(f"Authenticating arena with ID: {arena_id}")
                return Arena.objects.get(pk=arena_id)
            except Arena.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        try:
            return Arena.objects.get(pk=user_id)
        except Arena.DoesNotExist:
            return None
