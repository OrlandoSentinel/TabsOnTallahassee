from django.db import models
from django.contrib.auth.models import User


class EmailRecord(models.Model):
    user = models.ForeignKey(User, related_name='email_tasks')
    bills = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} updates for {} [{}]'.format(self.updates,
                                               self.user,
                                               self.created_at,
                                               )
