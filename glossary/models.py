from django.db import models


class Term(models.Model):
    term = models.CharField(max_length=250)
    definition = models.TextField()