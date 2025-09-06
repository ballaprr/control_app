from django.contrib.auth.backends import BaseBackend
from user.models import User

class UserAuthenticationBackend(BaseBackend):
    def authenticate(self, request, arena_name=None):
        if request is None:
            return None
        
        # Extract the arena_id from the request.session
        arena_id = request.session.get('user_id', None)
        if arena_id:
            try:
                print(f"Authenticating arena with ID: {arena_id}")
                return User.objects.get(pk=arena_id)
            except User.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
