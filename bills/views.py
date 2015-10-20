import string

from django.db.models import Q
from django.shortcuts import render, redirect

from tot import settings
from preferences.views import _mark_selected, _get_current_people
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

    sorted_bills = sort_bills_by_keyword(bills)

    return render(
        request,
        'bills/all.html',
        {'bills': sorted_bills, 'subjects': subjects, 'current_session': current_session.name, 'letters': all_letters, 'alphalist': alphalist}
    )


def latest_bill_activity(request):
    user = request.user

    if user.is_anonymous():
        senators = _get_current_people(position='senator')
        representatives = _get_current_people(position='representative')
        locations = get_all_locations()
        subjects = get_all_subjects()

        request.session['filters'] = request.session.get('filters', {})
        request.session['filters']['senators'] = request.session['filters'].get('senators', [])
        request.session['filters']['representatives'] = request.session['filters'].get('representatives', [])
        request.session['filters']['locations'] = request.session['filters'].get('locations', [])
        request.session['filters']['subjects'] = request.session['filters'].get('subjects', [])

        if request.method == 'POST':
            request.session['filters'] = {}
            request.session['filters']['senators'] = request.POST.getlist('senators')
            request.session['filters']['representatives'] = request.POST.getlist('representatives')
            request.session['filters']['locations'] = request.POST.getlist('locations')
            request.session['filters']['subjects'] = request.POST.getlist('subjects')
            return redirect('.')

        marked_senators = _mark_selected(senators, request.session['filters']['senators'])
        marked_representatives = _mark_selected(representatives, request.session['filters']['representatives'])
        marked_locations = _mark_selected(locations, request.session['filters']['locations'])
        marked_subjects = _mark_selected(subjects, request.session['filters']['subjects'])

        filters_exist = ''.join([value for key, value in request.session['filters'].items()][0])

        if filters_exist:
            organized_subjects, organized_locations = filter_organize_bills(
                request.session['filters']['subjects'],
                request.session['filters']['locations']
            )
            bills = organized_subjects.copy()
            bills.update(organized_locations)
        else:
            bills = organize_bill_info(Bill.objects.filter(legislative_session=current_session))

        sorted_bills = sort_bills_by_keyword(bills)

        context = {
            'bills': sorted_bills,
            'current_session': current_session.name,
            'senators': marked_senators,
            'representatives': marked_representatives,
            'subjects': marked_subjects,
            'locations': marked_locations,
            'are_filters': filters_exist
        }

    else:
        # people_followed = PersonFollow.objects.filter(user=user)
        topics_followed = [item.topic for item in TopicFollow.objects.filter(user=user)]
        locations_followed = [item.location for item in LocationFollow.objects.filter(user=user)]

        organized_subjects, organized_locations = filter_organize_bills(topics_followed, locations_followed)

        bills = organized_subjects.copy()
        bills.update(organized_locations)

        sorted_bills = sort_bills_by_keyword(bills)

        context = {
            'bills': sorted_bills,
            'current_session': current_session.name
        }

    return render(request, 'bills/latest.html', context)


def sort_bills_by_keyword(bills):
    real_bills = []
    for keyword, bill_list in bills.items():
        real_bills.append({'name': keyword, 'sorter': keyword[0].lower(), 'bills': bill_list})

    return sorted(real_bills, key=lambda x: x["name"])


def organize_bill_info(all_bills, sorter='subject'):
    bills = {}
    for bill in all_bills:
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


def filter_organize_bills(topics_followed, locations_followed):
    topic_bills = []
    location_bills = []

    subj_q = Q()
    if topics_followed:
        for subject in topics_followed:
            subj_q |= Q(subject__contains=[subject])
        topic_bills = Bill.objects.filter(subj_q, legislative_session=current_session)

    location_q = Q()
    if locations_followed:
        for location in locations_followed:
            location_q |= Q(extras__places__contains=[location])
        location_bills = Bill.objects.filter(location_q, legislative_session=current_session)

    organized_subjects = organize_bill_info(topic_bills)
    organized_locations = organize_bill_info(all_bills=location_bills, sorter='location')

    return organized_subjects, organized_locations
