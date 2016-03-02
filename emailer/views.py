from django.shortcuts import render, get_object_or_404
from .models import EmailRecord

def unsubscribe(request, guid):
    print(guid)
    er = get_object_or_404(EmailRecord, unsubscribe_guid=guid)

    if request.method == 'GET':
        unsubscribed = (er.user.preferences.email_frequency == 'N')
    elif request.method == 'POST':
        er.user.preferences.email_frequency = 'N'
        er.user.preferences.save()
        unsubscribed = True

    return render(request, 'email/unsubscribe.html',
                  {'user': er.user,
                   'unsubscribed': unsubscribed,
                   })
