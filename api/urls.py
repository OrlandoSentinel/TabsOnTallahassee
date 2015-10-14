from rest_framework import routers
from . import views
from django.conf.urls import url, include


urlpatterns = [
    url(r'^people/$', views.PersonList.as_view()),
    url(r'^(?P<pk>ocd-person/.+)/$', views.PersonDetail.as_view(), name='person-detail'),
]
