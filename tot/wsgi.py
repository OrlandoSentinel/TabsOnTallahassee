"""
WSGI config for tot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""
import os

try:
    import newrelic.agent
    newrelic.agent.initialize(os.path.join(
        os.path.dirname(__file__),
        'newrelic.ini'
    ))
except Exception as e:
    print("newrelic couldn't be initialized:", e)

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tot.settings")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
