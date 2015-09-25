import uuid
from django.db import models
from django.contrib.auth.models import User
from opencivicdata.models.people_orgs import Person


class Preferences(models.Model):
    user = models.OneToOneField(User, related_name='preferences')

    street_line1 = models.CharField(max_length = 100, blank = True)
    street_line2 = models.CharField(max_length = 100, blank = True)
    zipcode = models.CharField(max_length = 5, blank = True)
    city = models.CharField(max_length = 100, blank = True)
    state = models.CharField(max_length = 100, blank = True)

    # api
    apikey = models.UUIDField(default=uuid.uuid4)
