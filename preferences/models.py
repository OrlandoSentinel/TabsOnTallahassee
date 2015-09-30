import uuid
from django.db import models
from django.contrib.auth.models import User
from opencivicdata.models.people_orgs import Person

from django.contrib.auth.models import User


class Preferences(models.Model):
    user = models.OneToOneField(User, related_name='preferences')
    address = models.CharField(max_length=100, blank=True)
    apikey = models.UUIDField(default=uuid.uuid4)


class PersonFollow(models.Model):
    user = models.ForeignKey(User, related_name='person_follows')
    person = models.ForeignKey(Person, related_name='follows')


class TopicFollow(models.Model):
    user = models.ForeignKey(User, related_name='topic_follows')
    topic = models.CharField(max_length=100)


class LocationFollow(models.Model):
    user = models.ForeignKey(User, related_name='location_follows')
    location = models.CharField(max_length=100)
