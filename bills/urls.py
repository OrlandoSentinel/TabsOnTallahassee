from . import views
from django.conf.urls import url


urlpatterns = [
    url(r'^by_topic/', views.bill_list_by_topic, name='by_topic'),
    url(r'^by_location', views.bill_list_by_location, name='by_location'),
    url(r'^by_legislator', views.bill_list_by_legislator, name='by_legislator'),
    url(r'^current_session/', views.bill_list_current_session, name='current_session'),
    url(r'^latest_activity/', views.bill_list_latest, name='latest'),
    url(r'^detail/(?P<bill_session>(.*))/(?P<bill_identifier>(.*))/$', views.bill_detail, name='bill_detail'),
]
