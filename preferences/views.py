import json
import requests
from tot import settings

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from opencivicdata.models import Organization
from bills.utils import get_all_subjects, get_all_locations
from preferences.models import PersonFollow, LocationFollow, TopicFollow, Preferences
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail


def _get_current_people(position):
    if position == 'senator':
        return Organization.objects.get(name='Florida Senate').get_current_members()
    if position == 'representative':
        return Organization.objects.get(name='Florida House of Representatives').get_current_members()


def _mark_selected(items, items_followed):
    selected_items = []
    for item in items:
        item_dict = {}
        item_dict['item'] = item
        if item in items_followed:
            item_dict['selected'] = True
        else:
            item_dict['selected'] = False
        selected_items.append(item_dict)

    return selected_items


class EmailRegistrationView(RegistrationView):
    form_class = RegistrationFormUniqueEmail


def user_preferences(request):
    user = request.user

    senators = _get_current_people(position='senator')
    representatives = _get_current_people(position='representative')
    locations = get_all_locations()
    subjects = get_all_subjects()

    people_followed = [individual.person for individual in PersonFollow.objects.filter(user=user)]
    subjects_followed = [subject.topic for subject in TopicFollow.objects.filter(user=user)]
    locations_followed = [location.location for location in LocationFollow.objects.filter(user=user)]

    selected_reps = _mark_selected(representatives, people_followed)
    selected_senators = _mark_selected(senators, people_followed)
    selected_subjects = _mark_selected(subjects, subjects_followed)
    selected_locations = _mark_selected(locations, locations_followed)

    preferences = get_object_or_404(Preferences, user=user) or Preferences.objects.create(user=user)
    error_message = None
    address_senator = None
    address_representative = None
    if preferences.sen_from_address and preferences.rep_from_address:
        address_senator = json.loads(preferences.sen_from_address)
        address_representative = json.loads(preferences.rep_from_address)
        if address_senator['name'] == 'none found':
            error_message = 'No senators could be found for your query: Please make sure you have entered a valid FL address'

    if request.method == 'POST':
        with transaction.atomic():
            PersonFollow.objects.filter(user=user).delete()
            TopicFollow.objects.filter(user=user).delete()
            LocationFollow.objects.filter(user=user).delete()
            for senator in request.POST.getlist('senators'):
                PersonFollow.objects.create(user=user, person_id=senator)
            for representative in request.POST.getlist('representatives'):
                PersonFollow.objects.create(user=user, person_id=representative)
            for location in request.POST.getlist('locations'):
                LocationFollow.objects.create(user=user, location=location)
            for subject in request.POST.getlist('subjects'):
                TopicFollow.objects.create(user=user, topic=subject)

        return redirect('.')

    return render(
        request,
        'preferences/preferences.html',
        {
            'user': user,
            'senators': selected_senators,
            'representatives': selected_reps,
            'locations': selected_locations,
            'subjects': selected_subjects,
            'address': preferences.address,
            'address_senator': address_senator,
            'address_representative': address_representative,
            'error_message': error_message
        }
    )


@login_required
def set_user_latlon(request):
    user = request.user
    request.session = {}
    if request.is_ajax():
        lat = request.GET.get('lat', '')
        lon = request.GET.get('lon', '')
        address = request.GET.get('address', '')
        preferences = get_object_or_404(Preferences, user=user) or Preferences.objects.create(user=user)
        apikey = str(preferences.apikey)
        preferences.lat = float(lat)
        preferences.lon = float(lon)
        preferences.address = address

        api_resp = requests.get(
            settings.DOMAIN + '/api/people/?latitude={}&longitude={}&apikey={}'.format(
                preferences.lat, preferences.lon, apikey
            )
        ).json()
        if api_resp['meta']['pagination']['count'] == 2:
            for person in api_resp['data']:
                if 'Senators' in person['attributes']['image']:
                    senator = {'name': person['attributes']['name'], 'url': person['links']['self'], 'id': person['id']}
                    preferences.sen_from_address = json.dumps(senator)
                else:
                    representative = {'name': person['attributes']['name'], 'url': person['links']['self'], 'id': person['id']}
                    preferences.rep_from_address = json.dumps(representative)
        else:
            preferences.sen_from_address = preferences.rep_from_address = json.dumps({'name': 'none found'})

        preferences.save()

        PersonFollow.objects.create(user=user, person_id=senator['id'])
        PersonFollow.objects.create(user=user, person_id=representative['id'])

    return redirect(user_preferences)
