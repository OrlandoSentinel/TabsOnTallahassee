from django.contrib import admin
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from preferences.views import EmailRegistrationView, user_preferences, set_user_latlon
from bills.views import bill_list, latest_bill_activity
from django.contrib.flatpages import views as flatpages_views


admin.site.site_header = 'Tabs on Tallahassee Admin'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^glossary/', include('glossary.urls')),
    url('^', include('django.contrib.auth.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^accounts/register/', EmailRegistrationView.as_view(), name='registration_register'),
    url(r'^preferences/', user_preferences, name='preferences'),
    url(r'^set_user_latlon/', set_user_latlon, name='set_user_latlon'),
    url(r'^bills/', bill_list, name='bills_list'),
    url(r'^latest/', latest_bill_activity, name='latest_bill_activity'),
    url(r'^admin/', include('opencivicdata.admin.urls')),

    # flatpages
    url(r'^$', flatpages_views.flatpage, {'url': '/'}, name='home'),
    url(r'^about/$', flatpages_views.flatpage, {'url': '/about/'}, name='about'),
    url(r'^api/$', flatpages_views.flatpage, {'url': '/api/'}, name='api-docs'),
]

urlpatterns += staticfiles_urlpatterns()
set_user_latlon
