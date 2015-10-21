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

from preferences.views import EmailRegistrationView, user_preferences
from bills.views import bill_list, latest_bill_activity
from home import views
from django.contrib.flatpages import views as flatpages_views


admin.site.site_header = 'Tabs on Tallahassee Admin'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^glossary/', include('glossary.urls')),
    url('^', include('django.contrib.auth.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/register/', EmailRegistrationView.as_view(), name= 'registration_register'),
    url(r'^preferences/', user_preferences, name='preferences'),
    url(r'^$', 'home.views.index'),
    url(r'^about/', 'home.views.about'),
    url(r'^bills/', bill_list, name='bills_list'),
    url(r'^latest/', latest_bill_activity, name='latest_bill_activity'),
    url(r'^admin/', include('opencivicdata.admin.urls')),

    # flatpages
    url(r'^api/$', flatpages_views.flatpage, {'url': '/api/'}, name='api-docs'),
]

urlpatterns += staticfiles_urlpatterns()
