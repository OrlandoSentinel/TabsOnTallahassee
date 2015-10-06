
from django.db import transaction
from django.shortcuts import render, redirect

from tot import settings
from preferences.views import _mark_selected
from bills.utils import get_all_subjects, get_all_locations

from opencivicdata.models import Bill, LegislativeSession

current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

def bill_list(request):

    subjects = get_all_subjects()

    if request.POST.getlist('bill_subjects'):
        filter_subjects = request.POST.getlist('bill_subjects')
        all_bills = Bill.objects.filter(legislative_session=current_session, subject__contains=filter_subjects).order_by("title")
    else:
        filter_subjects = []
        all_bills = Bill.objects.filter(legislative_session=current_session).order_by("title")

    subjects = _mark_selected(subjects, filter_subjects)

    bills = {}
    for bill in all_bills:
        bill_locations = bill.extras['places']

        bill_detail = {}
        bill_detail['title'] = bill.title
        bill_detail['startswith'] = bill.title[0].lower()
        bill_detail['from_organization'] = bill.from_organization.name
        bill_detail['legislative_session'] = bill.legislative_session.name
        bill_detail['subject'] = bill.subject
        bill_detail['actions'] = []
        bill_detail['sponsorships'] = []
        bill_detail['locations'] = bill.extras['places']

        for action in bill.actions.all():
            bill_detail['actions'].append({'description': action.description, 'date': action.date})

        for sponsorship in bill.sponsorships.all():
            bill_detail['sponsorships'].append({
                'sponsor': sponsorship.name,
                'id': sponsorship.id,
                'primary': sponsorship.primary
            })

        for subject in bill.subject:
            if subject in bills.keys():
                bills[subject].append(bill_detail)
            else:
                bills[subject] = [bill_detail]

    real_bills = []
    for keyword,bill_list in bills.items():
        real_bills.append({'name': keyword, 'sorter': keyword[0].lower(), 'bills': bill_list})

    items = sorted(real_bills, key = lambda x: x["name"])

    return render(
        request,
        'bills/all.html',
        {'bills': items, 'subjects': subjects, 'current_session': current_session.name}
    )
