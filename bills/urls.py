from . import views
from django.conf.urls import url


urlpatterns = [
    url(r'^by_topic/', views.bill_list_by_topic),
    url(r'^by_location', views.bill_list_by_location),
    url(r'^latest_activity/', views.latest_bill_activity),
    url(r'^latest/', views.latest_bill_actions),
    url(r'^detail/(?P<bill_id>(.*))/$', views.bill_detail, name='bill_detail'),
]
