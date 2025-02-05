from django.contrib.auth.backends import ModelBackend
from .models import CustomUser  # Import your custom user model

class PhoneNumberBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Assuming you are using phone_number instead of username for login
            user = CustomUser.objects.get(phone_number=username)
            if user.check_password(password):  # Check if password matches
                return user
        except CustomUser.DoesNotExist:
            return None
