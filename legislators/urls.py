from . import views
from django.conf.urls import url


urlpatterns = [
    url(r'^find_legislator/', views.find_legislator),
    url(r'^get_latlon/', views.get_latlon)
]
