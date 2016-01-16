from . import views
from django.conf.urls import url


urlpatterns = [
    url(r'^find_legislator/', views.find_legislator, name="find_legislator"),
    url(r'^get_latlon/', views.get_latlon, name="get_latlon"),
    url(r'^all_legislators/', views.all_legislators, name="all"),
    url(r'^latest_latlon/', views.latest_latlon, name="latest_latlon"),
    url(r'^detail/(?P<legislator_id>(.*))/$', views.legislator_detail, name='legislator_detail')
]
