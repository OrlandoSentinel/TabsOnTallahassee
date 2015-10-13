from django.http import HttpResponse
from .models import Preferences


class AuthMiddleware:
    def process_request(self, request):
        PROTECTED = ('/api/',
                     )
        if request.get_full_path().startswith(PROTECTED):
            request.GET = request.GET.copy()
            apikey = (request.META.get('X-APIKEY') or
                      request.GET.pop('apikey', None))
            if isinstance(apikey, list):
                apikey = apikey[0]

            try:
                p = Preferences.objects.get(apikey=apikey)
            except (Preferences.DoesNotExist, ValueError) as e:
                if apikey:
                    return HttpResponse('{"message": "invalid API key"}',
                                        status=403)
                else:
                    return HttpResponse('{"message": "missing API key"}',
                                        status=403)
