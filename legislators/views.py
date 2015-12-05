import json
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse

from opencivicdata.models import Person

from tot import settings


def find_legislator(request):
    senator = request.session.get('sen_from_address')
    representative = request.session.get('rep_from_address')
    address = request.session.get('address')
    lat = request.session.get('lat') or '30.4'
    lon = request.session.get('lon') or '-84.3'

    if senator and representative:
        senator = json.loads(senator)
        representative = json.loads(representative)

    return render(
        request,
        'legislators/find_legislator.html', {
            'address_senator': senator,
            'address_representative': representative,
            'address': address,
            'lat': float(lat),
            'lng': float(lon)
        }
    )


def legislator_detail(request, legislator_id):
    legislator = Person.objects.get(id=legislator_id)
    memberships = legislator.memberships.all()
    post = memberships.filter(post__isnull=False)[0]
    party = memberships.filter(organization__classification='party')[0].organization.name
    if party == 'Democratic':
        party = 'Democrat'

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

    return render(
        request,
        'legislators/detail.html',
        {
            'legislator': legislator,
            'contact_details': contact_details,
            'post': post.post,
            'party': party
        }
    )


def latest_latlon(request):
    # TODO - Fix so that it gets API info and does not refresh.
    return redirect('/#legislators')


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
