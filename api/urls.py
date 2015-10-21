from rest_framework import routers
from . import views
from django.conf.urls import url, include


urlpatterns = [
    url(r'^jurisdictions/$', views.JurisdictionList.as_view()),
    url(r'^(?P<pk>ocd-jurisdiction/.+)/$', views.JurisdictionDetail.as_view(), name='jurisdiction-detail'),
    url(r'^people/$', views.PersonList.as_view()),
    url(r'^(?P<pk>ocd-person/.+)/$', views.PersonDetail.as_view(), name='person-detail'),
    url(r'^organizations/$', views.OrganizationList.as_view()),
    url(r'^(?P<pk>ocd-organization/.+)/$', views.OrganizationDetail.as_view(), name='organization-detail'),
    url(r'^bills/$', views.BillList.as_view()),
    url(r'^(?P<pk>ocd-bill/.+)/$', views.BillDetail.as_view(), name='bill-detail'),
    url(r'^votes/$', views.VoteList.as_view()),
    url(r'^(?P<pk>ocd-vote/.+)/$', views.VoteDetail.as_view(), name='voteevent-detail'),
]

# Event, Post, Membership, Division
