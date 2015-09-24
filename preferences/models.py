from django.db import models

from opencivicdata.models.people_orgs import Person


class Preferences(models.Model):
    representitive = models.ForeignKey(Person, related_name='rep_preferences')
    senator = models.ForeignKey(Person, related_name='sen_preferences')

    street_line1 = models.CharField(max_length = 100, blank = True)
    street_line2 = models.CharField(max_length = 100, blank = True)
    zipcode = models.CharField(max_length = 5, blank = True)
    city = models.CharField(max_length = 100, blank = True)
    state = models.CharField(max_length = 100, blank = True)
