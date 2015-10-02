
from django.shortcuts import render, redirect

from bills.utils import get_all_subjects, get_all_locations

from opencivicdata.models import Bill

def bill_list(request):
    all_bills = Bill.objects.all()

    subjects = get_all_subjects()

    details = []
    for bill in all_bills:
        bill_detail = {}

        bill_detail['title'] = bill.title
        bill_detail['from_organization'] = bill.from_organization.name
        bill_detail['actions'] = []
        bill_detail['sponsorships'] = []

        for action in bill.actions.all():
            bill_detail['actions'].append({'description': action.description, 'date': action.date})

        for sponsorship in bill.sponsorships.all():
            bill_detail['sponsorships'].append({
                'sponsor': sponsorship.name,
                'id': sponsorship.id,
                'primary': sponsorship.primary
            })

        details.append(bill_detail)

    # import ipdb; ipdb.set_trace()

    return render(
        request,
        'bills/all.html',
        {'bills': details, 'subjects': subjects}
    )
