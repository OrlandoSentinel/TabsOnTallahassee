"""tot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from preferences.views import EmailRegistrationView, UserPreferences

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^glossary/', include('glossary.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/register/', EmailRegistrationView.as_view(), name= 'registration_register'),
    url(r'^preferences/', UserPreferences.as_view(), name='preferences')
]

urlpatterns += staticfiles_urlpatterns()
