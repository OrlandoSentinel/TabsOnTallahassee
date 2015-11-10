from . import views
from django.conf.urls import url


urlpatterns = [
    url(r'^list/', views.bill_list),
    url(r'^latest_activity/', views.latest_bill_activity),
    url(r'^latest/', views.latest_bill_actions),
    url(r'^detail/(?P<bill_id>(.*))/$', views.bill_detail, name='bill_detail'),
]
