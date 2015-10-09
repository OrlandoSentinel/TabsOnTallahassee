import string

from django.db import transaction
from django.shortcuts import render, redirect

from tot import settings
from preferences.views import _mark_selected
from bills.utils import get_all_subjects, get_all_locations
from preferences.models import PersonFollow, TopicFollow, LocationFollow

from opencivicdata.models import Bill, LegislativeSession

current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

all_letters = string.ascii_lowercase

def bill_list(request):
    alphalist = True
    subjects = get_all_subjects()

    if request.POST.getlist('bill_subjects'):
        filter_subjects = request.POST.getlist('bill_subjects')
        all_bills = Bill.objects.filter(legislative_session=current_session, subject__contains=filter_subjects).order_by("title")
    else:
        filter_subjects = []
        all_bills = Bill.objects.filter(legislative_session=current_session).order_by("title")

    subjects = _mark_selected(subjects, filter_subjects)

    bills = organize_bill_info(all_bills=all_bills, sorter='subject')

    real_bills = []
    for keyword,bill_list in bills.items():
        real_bills.append({'name': keyword, 'sorter': keyword[0].lower(), 'bills': bill_list})

    items = sorted(real_bills, key = lambda x: x["name"])

    return render(
        request,
        'bills/all.html',
        {'bills': items, 'subjects': subjects, 'current_session': current_session.name, 'letters': all_letters, 'alphalist': alphalist}
    )


def latest_bill_activity(request):
    alphalist = False
    topic_bills = []
    location_bills = []
    if not request.user.is_anonymous():
        user = request.user

        # people_followed = PersonFollow.objects.filter(user=user)
        topics_followed = [item.topic for item in TopicFollow.objects.filter(user=user)]
        locations_followed = [item.location for item in LocationFollow.objects.filter(user=user)]

        #  TODO - how do I make this not a loop?
        for subject in topics_followed:
            topic_bills += Bill.objects.filter(legislative_session=current_session, subject__contains=[subject])
        
        #  TODO - how do I actually do this query?
        # for location in locations_followed:
        #     location_bills += Bill.objects.filter(legislative_session=current_session, extras__contains=[location])
        location_bills = Bill.objects.filter(legislative_session=current_session, subject__contains=['insurance'])

        organized_subjects = organize_bill_info(topic_bills)
        organized_locations = organize_bill_info(all_bills=location_bills, sorter='location')

        bills = organized_subjects.copy()
        bills.update(organized_locations)

        real_bills = []
        for keyword,bill_list in bills.items():
            real_bills.append({'name': keyword, 'sorter': keyword[0].lower(), 'bills': bill_list})

        items = sorted(real_bills, key = lambda x: x["name"])

    return render(
        request,
        'bills/all.html',
        {'bills': items, 'current_session': current_session.name, 'letters': all_letters, 'alphalist': alphalist}
    )


def organize_bill_info(all_bills, sorter='subject'):
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

        if sorter == 'subject':
            for subject in bill.subject:
                if subject in bills.keys():
                    bills[subject].append(bill_detail)
                else:
                    bills[subject] = [bill_detail]
        if sorter == 'location':
            for location in bill.extras['places']:
                if location in bills.keys():
                    bills[location].append(bill_detail)
                else:
                    bills[location] = [bill_detail]

    return bills
