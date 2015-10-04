
from django.db import transaction
from django.shortcuts import render, redirect

from preferences.views import _mark_selected
from bills.utils import get_all_subjects, get_all_locations

from opencivicdata.models import Bill

def bill_list(request):

    subjects = get_all_subjects()

    if request.POST.getlist('bill_subjects'):
        filter_subjects = request.POST.getlist('bill_subjects')
        all_bills = Bill.objects.filter(subject__contains=filter_subjects)
    else:
        filter_subjects = []
        all_bills = Bill.objects.all()

    subjects = _mark_selected(subjects, filter_subjects)
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

    return render(
        request,
        'bills/all.html',
        {'bills': details, 'subjects': subjects}
    )
