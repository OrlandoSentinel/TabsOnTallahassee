
from django.shortcuts import render, redirect

from opencivicdata.models import Bill

def bill_list(request):
    all_bills = Bill.objects.all()

    details = []
    for bill in all_bills:
        bill_detail = {}

        bill_detail['title'] = bill.title
        bill_detail['from_organization'] = bill.from_organization.name
        bill_detail['actions'] = []

        for action in bill.actions.all():
            bill_detail['actions'].append({'description': action.description, 'date': action.date})

        details.append(bill_detail)

    return render(
        request,
        'bills/all.html',
        {'bills': details}
    )
