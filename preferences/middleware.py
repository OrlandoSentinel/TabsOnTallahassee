from django.core.exceptions import PermissionDenied
from .models import Preferences


class AuthMiddleware:
    def process_request(self, request):
        PROTECTED = ('/ocd-',
                     '/jurisdictions'
                     )
        if request.get_full_path().startswith(PROTECTED):
            request.GET = request.GET.copy()
            apikey = request.META.get('X-APIKEY') or request.GET.pop('apikey')
            if isinstance(apikey, list):
                apikey = apikey[0]

            try:
                p = Preferences.objects.get(apikey=apikey)
            except (Preferences.DoesNotExist, ValueError) as e:
                raise PermissionDenied('invalid api key')
