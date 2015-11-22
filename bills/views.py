import string
import requests

from django.db.models import Q
from django.shortcuts import render

from django.contrib.auth.models import User

from tot import settings
from preferences.views import _mark_selected, _get_current_people
from bills.utils import get_all_subjects, get_all_locations
from preferences.models import PersonFollow, TopicFollow, LocationFollow

from opencivicdata.models import Bill, LegislativeSession, Person

ALL_LETTERS = string.ascii_lowercase


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
            'letters': ALL_LETTERS,
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
            extras__places__contains=filter_locations
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
            'letters': ALL_LETTERS,
            'alphalist': alphalist
        }
    )


def bill_list_by_legislator(request):
    '''Sort bills based on Legislator that's the primary sponsor
    '''
    alphalist = True
    legislators = list(_get_current_people(position='senator'))
    legislators += list(_get_current_people(position='representative'))
    legislators = [person.name for person in legislators]
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

    if request.GET.getlist('bill_sorters'):
        filter_whole_legislators = request.GET.getlist('bill_sorters')
        filter_legislators = [name.split(',')[0].strip() for name in filter_whole_legislators]
        all_bills = Bill.objects.filter(
            legislative_session=current_session,
            sponsorships__name__in=filter_legislators
        ).order_by("title").prefetch_related('legislative_session')
    else:
        filter_whole_legislators = []
        all_bills = Bill.objects.filter(
            legislative_session=current_session
        ).order_by("title").prefetch_related('legislative_session', 'sponsorships')

    legislators = _mark_selected(legislators, filter_whole_legislators)

    bills = group_bills_by_sorter(all_bills=all_bills, sorter='legislator')

    sorted_bills = sort_bills_by_keyword(bills)

    return render(
        request,
        'bills/all.html',
        {
            'bills': sorted_bills,
            'sorter_type': 'legislator',
            'sorters': legislators,
            'current_session': current_session.name,
            'letters': ALL_LETTERS,
            'alphalist': alphalist
        }
    )


def bill_list_current_session(request):
    ''' List of all bills for the current session.
    Organized by latest action.
    '''
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)
    subjects = get_all_subjects()

    filters = {
        'legislative_session__name': settings.CURRENT_SESSION
    }

    filter_subjects = []
    search_text = ''

    if request.GET.getlist('subjects'):
        filter_subjects = request.GET.getlist('subjects')
        filters['subject__contains'] = filter_subjects

    if request.GET.get('search_text'):
        search_text = request.GET.get('search_text')
        filters['versions__links__text__ftsearch'] = search_text

    bills = Bill.objects.filter(**filters).order_by(
        '-actions__date').select_related('legislative_session').prefetch_related(
            'sponsorships', 'actions').distinct()  # [:settings.NUMBER_OF_LATEST_ACTIONS]

    # force DB query now and append latest_action to each bill
    # set is called first to remove duplicates - distinct does not work above because
    # of the 'order-by' paramater - that adds a field and causes distinct to not work as expected
    bills = set(bills)
    for bill in bills:
        # use all() so the prefetched actions can be used, could possibly impove
        # via smarter use of Prefetch()
        bill.latest_action = list(bill.actions.all())[-1]

    subjects = _mark_selected(subjects, filter_subjects)

    context = {
        'latest_bills': bills,
        'current_session': current_session.name,
        'subjects': subjects,
        'search_text': search_text
    }

    return render(
        request,
        'bills/current_session.html',
        context
    )


def get_user_preferences(user):
    user = User.objects.get(username=user)

    person_follows = [person['person_id'] for person in user.person_follows.values()]
    topic_follows = [topic['topic'] for topic in user.topic_follows.values()]
    location_follows = [location['location'] for location in user.location_follows.values()]

    return person_follows, topic_follows, location_follows


def bill_list_latest(request):
    ''' List of bills with a latest action for the current session, based on preferences.
    Organized by topic, legislator, topic, and then by latest action.
    '''
    user = request.user

    # TODO - add filters for non-logged in users
    current_session = LegislativeSession.objects.get(name=settings.CURRENT_SESSION)

    filters = {
        'legislative_session__name': settings.CURRENT_SESSION
    }

    all_bills = Bill.objects.filter(**filters).order_by(
        '-actions__date').select_related('legislative_session').prefetch_related(
            'sponsorships', 'actions')

    # This will be a list of dicts.
    # There will be one entry for each of the topics, locations,legislators followed.
    bills_by_selected_filter = []

    if not user.is_anonymous():
        people, topics, locations = get_user_preferences(user)

        if people:
            for person in people:
                person_name = Person.objects.get(id=person).name
                person_bills = all_bills.filter(sponsorships__id__contains=person)[:settings.NUMBER_OF_LATEST_ACTIONS]
                person_detail = {'heading': person_name, 'bills': person_bills}
                bills_by_selected_filter.append(person_detail)
        if topics:
            for topic in topics:
                topic_bills = all_bills.filter(subject__contains=[topic])[:settings.NUMBER_OF_LATEST_ACTIONS]
                topic_detail = {'heading': topic, 'bills': topic_bills}
                bills_by_selected_filter.append(topic_detail)

        # if locations:
        #     for location in locations:
        #         location_bills = all_bills.filter(extras__places__contains=location)
        #         location_detail = {'heading': location, 'bills': location_bills}
        #         bills_by_selected_filter.append(location_detail)

    for item in bills_by_selected_filter:
        for bill in item['bills']:
        # use all() so the prefetched actions can be used, could possibly impove
        # via smarter use of Prefetch()
            bill.latest_action = list(bill.actions.all())[-1]

    context = {
        'user': user,
        'bills_by_selected_filter': bills_by_selected_filter,
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
                check_add_to_dict(subject, bills, bill)
        elif sorter == 'location':
            for location in bill.extras['places']:
                check_add_to_dict(location, bills, bill)
        elif sorter == 'legislator':
            for sponsor in bill.sponsorships.all():
                check_add_to_dict(sponsor.name, bills, bill)

    return bills


def check_add_to_dict(key, dictionary, item):
    if key in dictionary.keys():
        dictionary[key].append(item)
    else:
        dictionary[key] = [item]


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
    # A way to see the text of the different versions of the bill. That information is also in the database. We like the way GovTrack does it in the history section when you click the “see changes” link and see the differences side by side.
    # A way to view the votes taken on a bill in the House and Senate. We like the way GovTrack does it — essentially just a glorified list: https://www.govtrack.us/congress/votes/114-2015/s272
