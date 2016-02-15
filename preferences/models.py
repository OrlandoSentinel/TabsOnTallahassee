import uuid
from django.db import models
from django.contrib.auth.models import User
from opencivicdata.models.people_orgs import Person

EMAIL_FREQUENCIES = (
    ('N', 'Never'),
    ('D', 'Daily'),
    ('W', 'Weekly'),
)

EMAIL_TYPES = (
    ('H', 'HTML'),
    ('T', 'Plain Text'),
)


class Preferences(models.Model):
    user = models.OneToOneField(User, related_name='preferences')
    address = models.CharField(max_length=100, blank=True, null=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    rep_from_address = models.CharField(max_length=255, blank=True, null=True)
    sen_from_address = models.CharField(max_length=255, blank=True, null=True)
    apikey = models.UUIDField(default=uuid.uuid4)

    # email preferences
    email_frequency = models.CharField(max_length=1, choices=EMAIL_FREQUENCIES,
                                       default='N')
    email_type = models.CharField(max_length=1, choices=EMAIL_TYPES,
                                  default='T')


class PersonFollow(models.Model):
    user = models.ForeignKey(User, related_name='person_follows')
    person = models.ForeignKey(Person, related_name='follows')


class TopicFollow(models.Model):
    user = models.ForeignKey(User, related_name='topic_follows')
    topic = models.CharField(max_length=100)


class LocationFollow(models.Model):
    user = models.ForeignKey(User, related_name='location_follows')
    location = models.CharField(max_length=100)
