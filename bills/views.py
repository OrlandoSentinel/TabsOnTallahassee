import string

from django.db.models import Q
from django.shortcuts import render

from tot import settings
from preferences.views import _mark_selected, _get_current_people
from bills.utils import get_all_subjects, get_all_locations
from preferences.models import PersonFollow, TopicFollow, LocationFollow

from opencivicdata.models import Bill, LegislativeSession

all_letters = string.ascii_lowercase


def bill_list_by_topic(request):
    alphalist = True
    subjects = get_all_subjects()
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

    if request.GET.getlist('bill_sorters'):
        filter_subjects = request.GET.getlist('bill_sorters')
        all_bills = Bill.objects.filter(
            legislative_session=current_session,
            subject__contains=filter_subjects
        ).order_by("title").prefetch_related('legislative_session')
    else:
        filter_subjects = []
        all_bills = Bill.objects.filter(
            legislative_session=current_session
        ).order_by("title").prefetch_related('legislative_session')

    subjects = _mark_selected(subjects, filter_subjects)

    bills = group_bills_by_sorter(all_bills=all_bills, sorter='subject')

    sorted_bills = sort_bills_by_keyword(bills)

    return render(
        request,
        'bills/all.html',
        {
            'bills': sorted_bills,
            'sorter_type': 'subject',
            'sorters': subjects,
            'current_session': current_session.name,
            'letters': all_letters,
            'alphalist': alphalist
        }
    )


def bill_list_by_location(request):
    '''Sort bills based on Location
    '''
    alphalist = True
    locations = get_all_locations()
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

    if request.GET.getlist('bill_sorters'):
        filter_locations = request.GET.getlist('bill_sorters')
        all_bills = Bill.objects.filter(
            legislative_session=current_session,
            subject__contains=filter_locations
        ).order_by("title").prefetch_related('legislative_session')
    else:
        filter_locations = []
        all_bills = Bill.objects.filter(
            legislative_session=current_session
        ).order_by("title").prefetch_related('legislative_session')

    locations = _mark_selected(locations, filter_locations)

    bills = group_bills_by_sorter(all_bills=all_bills, sorter='location')

    sorted_bills = sort_bills_by_keyword(bills)

    return render(
        request,
        'bills/all.html',
        {
            'bills': sorted_bills,
            'sorter_type': 'location',
            'sorters': locations,
            'current_session': current_session.name,
            'letters': all_letters,
            'alphalist': alphalist
        }
    )


def bill_list_current_session(request):
    ''' List of all bills for the current session.
    Organized by latest action.
    '''
    # TODO - add filters for non-logged in users
    # TODO - filter also based on logged in users preferences
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

    filters = {
        'legislative_session__name': settings.CURRENT_SESSION
    }

    bills = Bill.objects.filter(**filters).order_by(
        '-actions__date').select_related('legislative_session').prefetch_related(
            'sponsorships', 'actions')  # [:settings.NUMBER_OF_LATEST_ACTIONS]

    # force DB query now and append latest_action to each bill
    bills = list(bills)
    for bill in bills:
        # use all() so the prefetched actions can be used, could possibly impove
        # via smarter use of Prefetch()
        bill.latest_action = list(bill.actions.all())[-1]

    context = {
        'latest_bills': bills,
        'current_session': current_session.name
    }

    return render(
        request,
        'bills/latest_actions.html',
        context
    )


def bill_list_latest(request):
    ''' List of bills with a latest action for the current session.
    Organized by latest action.
    '''
    # TODO - add filters for non-logged in users
    # TODO - filter also based on logged in users preferences
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

    filters = {
        'legislative_session__name': settings.CURRENT_SESSION
    }

    bills = Bill.objects.filter(**filters).order_by(
        '-actions__date').select_related('legislative_session').prefetch_related(
            'sponsorships', 'actions')[:settings.NUMBER_OF_LATEST_ACTIONS]

    # force DB query now and append latest_action to each bill
    bills = list(bills)
    for bill in bills:
        # use all() so the prefetched actions can be used, could possibly impove
        # via smarter use of Prefetch()
        bill.latest_action = list(bill.actions.all())[-1]

    context = {
        'latest_bills': bills,
        'current_session': current_session.name
    }

    return render(
        request,
        'bills/latest_actions.html',
        context
    )


def group_bills_by_sorter(all_bills, sorter='subject'):
    ''' Takes a queryset of bills.
    Adds locations and startswith to bill object
    Returns a dict of bills sorted by location or subject,
    dependng on the sorter.
    This is done to add the bill to the list for each subject and
    location its attached to.
    '''
    bills = {}
    for bill in all_bills:
        bill.locations = bill.extras['places']
        bill.startswith = bill.title[0].lower()

        if sorter == 'subject':
            for subject in bill.subject:
                if subject in bills.keys():
                    bills[subject].append(bill)
                else:
                    bills[subject] = [bill]
        if sorter == 'location':
            for location in bill.extras['places']:
                if location in bills.keys():
                    bills[location].append(bill)
                else:
                    bills[location] = [bill]

    return bills


def sort_bills_by_keyword(bills):
    ''' Prepare the bills to go into the view.
    Sorts them, and makes sure there's a sorter for the template to use
    to render the correct list
    '''
    real_bills = []
    for keyword, bill_list in bills.items():
        real_bills.append({'name': keyword, 'sorter': keyword[0].lower(), 'bills': bill_list})

    return sorted(real_bills, key=lambda x: x["name"])


def filter_organize_bills(topics_followed, locations_followed):
    ''' Takes a list of topics you follow and locations you follow, and filters
    a bill set based on those topics and locations.
    Returns a tuple with those querysets of bills.
    '''
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

    organized_subjects = group_bills_by_sorter(topic_bills)
    organized_locations = group_bills_by_sorter(all_bills=location_bills, sorter='location')

    return organized_subjects, organized_locations


def bill_detail(request, bill_session, bill_identifier):
    bill = Bill.objects.get(legislative_session__identifier=bill_session, identifier=bill_identifier)

    sponsors = bill.sponsorships.all().select_related('person', 'organization')

    for sponsor in sponsors:
        sponsor.party = sponsor.person.memberships.filter(
            organization__classification='party'
        )[0].organization.name

    history = bill.actions.all()

    documents = bill.documents.all()
    versions = bill.versions.all()

    votes = bill.votes.all()

    context = {
        'bill': bill,
        'sponsors': sponsors,
        'history': history,
        'documents': documents,
        'versions': versions,
        'votes': votes
    }

    return render(
        request,
        'bills/detail.html',
        context
    )

    # If there's no information then have a message that says no information for now
    # Documents related to the bill (also from database)
    # Subjects the bill touches (also from the database)
    # Locations the bill touches (also from the database)
    # A way to see the text of the different versions of the bill. That information is also in the database. We like the way GovTrack does it in the history section when you click the “see changes” link and see the differences side by side.
    # A way to view the votes taken on a bill in the House and Senate. We like the way GovTrack does it — essentially just a glorified list: https://www.govtrack.us/congress/votes/114-2015/s272
