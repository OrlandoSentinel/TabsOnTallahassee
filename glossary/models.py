from django.db import models


class Term(models.Model):
    term = models.CharField(max_length=250)
    definition = models.TextField()

    def __str__(self):
        return self.term
