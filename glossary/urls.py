from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from . import views


urlpatterns = [
    url(r'^$', views.glossary, name='glossary'),
    url(r'^json/$', views.glossary_json, name='glossary_json'),
]

urlpatterns += staticfiles_urlpatterns()
