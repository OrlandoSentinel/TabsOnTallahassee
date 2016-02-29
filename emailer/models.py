import uuid
from django.db import models
from django.contrib.auth.models import User


class EmailRecord(models.Model):
    user = models.ForeignKey(User, related_name='email_tasks')
    bills = models.PositiveIntegerField()
    unsubscribe_guid = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} updates for {} [{}]'.format(self.bills,
                                               self.user,
                                               self.created_at,
                                               )
