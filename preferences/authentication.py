from rest_framework import authentication
from rest_framework import exceptions
from .models import Preferences


class KeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        apikey = (request.META.get('HTTP_X_APIKEY') or
                  request.GET.get('apikey', None))
        if isinstance(apikey, list):
            apikey = apikey[0]

        if not apikey:
            return None

        try:
            p = Preferences.objects.get(apikey=apikey)
            return (p.user, None)
        except (Preferences.DoesNotExist, ValueError) as e:
            raise exceptions.AuthenticationFailed('Invalid Key')
