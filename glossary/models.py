from django.db import models


class Glossary(models.Model):
    term = models.CharField(max_length=250)
    definition = models.TextField()