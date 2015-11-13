import string

from django.db.models import Q
from django.shortcuts import render, redirect

from tot import settings
from preferences.views import _mark_selected, _get_current_people
from bills.utils import get_all_subjects, get_all_locations
from preferences.models import PersonFollow, TopicFollow, LocationFollow

from opencivicdata.models import Bill, LegislativeSession, BillAction

all_letters = string.ascii_lowercase


def bill_list_by_topic(request):
    alphalist = True
    subjects = get_all_subjects()
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

    if request.POST.getlist('bill_sorters'):
        filter_subjects = request.POST.getlist('bill_sorters')
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
        {'bills': sorted_bills, 'sorter_type': 'subject', 'sorters': subjects, 'current_session': current_session.name, 'letters': all_letters, 'alphalist': alphalist}
    )


def bill_list_by_location(request):
    '''Sort bills based on Location
    '''
    alphalist = True
    locations = get_all_locations()
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

    if request.POST.getlist('bill_sorters'):
        filter_locations = request.POST.getlist('bill_sorters')
        all_bills = Bill.objects.filter(legislative_session=current_session, subject__contains=filter_locations).order_by("title")
    else:
        filter_locations = []
        all_bills = Bill.objects.filter(legislative_session=current_session).order_by("title")

    locations = _mark_selected(locations, filter_locations)

    bills = organize_bill_info(all_bills=all_bills, sorter='location')

    sorted_bills = sort_bills_by_keyword(bills)

    return render(
        request,
        'bills/all.html',
        {'bills': sorted_bills, 'sorter_type': 'location', 'sorters': locations, 'current_session': current_session.name, 'letters': all_letters, 'alphalist': alphalist}
    )


def latest_bill_actions(request):
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)
    latest_actions = BillAction.objects.all().select_related('bill')

    latest_bills = []
    for action in latest_actions[:settings.NUMBER_OF_LATEST_ACTIONS]:
        bill = action.bill
        bill_detail = {}
        sponsorships = bill.sponsorships.values()

        sponsors = []
        for sponsor in sponsorships:
            sponsors.append(sponsor.get('name'))

        bill_detail['bill_id'] = bill.id
        bill_detail['title'] = bill.title
        bill_detail['sponsors'] = sponsors
        bill_detail['identifier'] = bill.identifier
        bill_detail['latest_action'] = action.classification

        latest_bills.append(bill_detail)

    context = {
        'latest_bills': latest_bills,
        'current_session': current_session.name
    }

    return render(
        request,
        'bills/latest_actions.html',
        context
    )


def latest_bill_activity(request):
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)
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
    for bill in all_bills[:settings.NUMBER_OF_LATEST_ACTIONS]:
        bill_detail = {}
        bill_detail['title'] = bill.title
        bill_detail['identifier'] = bill.identifier
        bill_detail['id'] = bill.id
        bill_detail['startswith'] = bill.title[0].lower()
        bill_detail['from_organization'] = bill.from_organization.name
        bill_detail['legislative_session'] = bill.legislative_session.name
        bill_detail['session'] = bill.legislative_session
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
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

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


def bill_detail(request, bill_session, bill_identifier):
    bill = Bill.objects.get(legislative_session=bill_session, identifier=bill_identifier)

    sponsor_objects = bill.sponsorships.all()
    sponsors = []
    for sponsor in sponsor_objects:
        sponsor_detail = {}
        sponsor_detail['name'] = sponsor.name
        sponsor_detail['primary'] = sponsor.primary
        if sponsor.person:
            sponsor_detail['image'] = sponsor.person.image
            sponsor_detail['party'] = sponsor.person.memberships.organization.name
            sponsor_detail['district'] = sponsor.person.memberships.organization.jurisdiction.name

        sponsors.append(sponsor_detail)

    history = ['TO', 'DO']
    versions = bill.versions.all()

    vote_objects = bill.votes.all()
    votes = []
    for vote in vote_objects:
        vote_detail = {}
        vote_detail['count'] = vote.counts.value
        votes.append(vote_detail)

    context = {
        'identifier': bill.identifier,
        'summary': bill.title,
        'sponsors': sponsors,
        'history': history,
        'subjects': bill.subject,
        'locations': bill.extras.get('places'),
        'versions': versions,
        'votes': votes
    }

    return render(
        request,
        'bills/detail.html',
        context
    )

    # If there's no information then have a message that says no information for now
    # Bill title
    # Bill summary
    # Bill sponsor(s) with photo, party and district represented
    # Bill co-sponsor(s) with photo, party and district represented
    # Bill history (pulling from the list of actions in the database James is building), pretty much the same way GovTrack does it with the timeline approach
    # Documents related to the bill (also from database)
    # Subjects the bill touches (also from the database)
    # Locations the bill touches (also from the database)
    # A way to see the text of the different versions of the bill. That information is also in the database. We like the way GovTrack does it in the history section when you click the “see changes” link and see the differences side by side.
    # A way to view the votes taken on a bill in the House and Senate. We like the way GovTrack does it — essentially just a glorified list: https://www.govtrack.us/congress/votes/114-2015/s272
