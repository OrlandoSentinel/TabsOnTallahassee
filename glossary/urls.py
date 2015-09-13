from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from . import views


urlpatterns = [
    url(r'^$', views.glossary, name='glossary')
]

urlpatterns += staticfiles_urlpatterns()
