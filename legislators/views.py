import json
import requests
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from opencivicdata.models import Person

from tot import settings
from preferences.models import PersonFollow
from preferences.views import _get_current_people


def find_legislator(request):
    senator = request.session.get('sen_from_address')
    representative = request.session.get('rep_from_address')
    address = request.session.get('address')
    lat = request.session.get('lat') or '30.4'
    lon = request.session.get('lon') or '-84.3'

    senator_contact_details = None
    representative_contact_details = None
    senator_sponsorships = None
    rep_sponsorships = None

    if senator and representative:
        senator = json.loads(senator)
        if senator['name'] != 'none found':
            senator_obj = Person.objects.get(id=senator['id'])
            senator_contact_details = get_contact_details(senator_obj)
            senator_sponsorships = senator_obj.billsponsorship_set.all().prefetch_related(
                'bill'
            ).prefetch_related(
                'bill__legislative_session'
            )[:settings.NUMBER_OF_LATEST_ACTIONS]

        representative = json.loads(representative)
        if representative['name'] != 'none found':
            rep_obj = Person.objects.get(id=representative['id'])
            representative_contact_details = get_contact_details(rep_obj)
            rep_sponsorships = rep_obj.billsponsorship_set.all().prefetch_related(
                'bill'
            ).prefetch_related(
                'bill__legislative_session'
            )[:settings.NUMBER_OF_LATEST_ACTIONS]
    return render(
        request,
        'legislators/find_legislator.html', {
            'address_senator': senator,
            'address_representative': representative,
            'address': address,
            'lat': float(lat),
            'lng': float(lon),
            'senator_contact_details': senator_contact_details,
            'representative_contact_details': representative_contact_details,
            'rep_sponsorships': rep_sponsorships,
            'senator_sponsorships': senator_sponsorships
        }
    )


def get_contact_details(legislator):
    # Parsed out seperately for nicer rendering in the templates
    raw_contact_details = legislator.contact_details.all()
    contact_details = {'email': '', 'capitol': [], 'district': []}
    for entry in raw_contact_details:
        if entry.type == 'email':
            contact_details['email'] = entry.value
        if entry.note == 'capitol':
            contact_details['capitol'].append(entry)
        if entry.note == 'district':
            contact_details['district'].append(entry)

    return contact_details


def legislator_detail(request, legislator_id):
    legislator = Person.objects.get(id=legislator_id)
    memberships = list(legislator.memberships.all().select_related(
        'organization__classification'
    ).select_related('post'))
    post = [m for m in memberships if m.post][0]
    party = [m for m in memberships if m.organization.classification == 'party'][0].organization.name
    if party == 'Democratic':
        party = 'Democrat'

    contact_details = get_contact_details(legislator)

    all_votes = legislator.votes.all().prefetch_related(
        'vote_event__bill__legislative_session'
    ).order_by(
        '-vote_event__start_date'
    )

    paginator = Paginator(all_votes, 10)
    page = request.GET.get('page')

    try:
        votes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        votes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        votes = paginator.page(paginator.num_pages)

    recent_votes = votes[:settings.NUMBER_OF_LATEST_ACTIONS]
    sponsored_bills = [
        sponsorship.bill for sponsorship in legislator.billsponsorship_set.all().select_related(
            'bill__legislative_session'
        ).prefetch_related(
            'bill__actions', 'bill__sponsorships', 'bill__sponsorships__person'
        )
    ]
    for bill in sponsored_bills:
        bill.latest_action = list(bill.actions.all())[-1]

    message = ''
    if request.method == 'POST':
        try:
            PersonFollow.objects.get(user=request.user, person_id=legislator_id)
            message = 'You are already following {}.'.format(legislator.name)
        except PersonFollow.DoesNotExist:
            PersonFollow.objects.create(user=request.user, person_id=legislator_id)
            message = 'You are now following {}.'.format(legislator.name)

    return render(
        request,
        'legislators/detail.html',
        {
            'legislator': legislator,
            'contact_details': contact_details,
            'post': post.post,
            'party': party,
            'votes': votes,
            'recent_votes': recent_votes,
            'sponsored_bills': sponsored_bills,
            'message': message,
        }
    )


def all_legislators(request):
    senators = _get_current_people(position='senator').prefetch_related('memberships__post')
    representatives = _get_current_people(position='representative').prefetch_related('memberships__post')

    for senator in senators:
        memberships = senator.memberships.all()
        senator.district = [m for m in memberships if m.post][0]

    for representative in representatives:
        memberships = representative.memberships.all()
        representative.district = [m for m in memberships if m.post][0]

    return render(
        request,
        'legislators/all.html',
        {
            'senators': senators,
            'representatives': representatives
        }
    )


def latest_latlon(request):
    apikey = settings.ANON_API_KEY
    lat = request.GET.get('lat', '')
    lon = request.GET.get('lon', '')
    api_resp = requests.get(
        settings.DOMAIN + '/api/people/?latitude={}&longitude={}&apikey={}'.format(
            lat, lon, apikey
        )
    ).json()

    legislator_information = {}
    if api_resp.get('meta'):
        if api_resp['meta']['pagination']['count'] == 2:
            for person in api_resp['data']:
                person_dict = {
                    'name': person['attributes']['name'],
                    'url': person['links']['self'],
                    'id': person['id'],
                    'image': person['attributes']['image']
                }
                if 'Senators' in person['attributes']['image']:
                    legislator_information['address_senator'] = person_dict
                else:
                    legislator_information['address_representative'] = person_dict
    return render(
        request,
        'legislators/_geo_legislator_display.html',
        legislator_information
    )


def get_latlon(request):
    apikey = settings.ANON_API_KEY
    if request.is_ajax():
        lat = request.GET.get('lat', '')
        lon = request.GET.get('lon', '')
        address = request.GET.get('address', '')

        api_resp = requests.get(
            settings.DOMAIN + '/api/people/?latitude={}&longitude={}&apikey={}'.format(
                lat, lon, apikey
            )
        ).json()
        if api_resp.get('meta'):
            if api_resp['meta']['pagination']['count'] == 2:
                for person in api_resp['data']:
                    person_dict = {
                        'name': person['attributes']['name'],
                        'url': person['links']['self'],
                        'id': person['id'],
                        'image': person['attributes']['image']
                    }
                    if 'Senators' in person['attributes']['image']:
                        request.session['sen_from_address'] = json.dumps(person_dict)
                    else:
                        request.session['rep_from_address'] = json.dumps(person_dict)
            else:
                request.session['sen_from_address'] = request.session['rep_from_address'] = json.dumps({'name': 'none found'})

    request.session['lat'] = lat
    request.session['lon'] = lon
    request.session['address'] = address
    request.session.modified = True
    return redirect(find_legislator)
