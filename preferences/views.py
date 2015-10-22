import furl
import requests
from tot import settings

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from opencivicdata.models import Person, Organization
from bills.utils import get_all_subjects, get_all_locations
from preferences.models import PersonFollow, LocationFollow, TopicFollow, Preferences
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail


def _get_current_people(position):
    if position == 'senator':
        return Organization.objects.get(name='Florida Senate').get_current_members()
    if position == 'representative':
        return Organization.objects.get(name='Florida House of Representatives').get_current_members()


def _mark_selected(items, items_followed, from_location=False):
    selected_items = []
    for item in items:
        item_dict = {}
        item_dict['item'] = item
        item_dict['from_location'] = from_location
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

    if request.method == 'POST':
        with transaction.atomic():
            PersonFollow.objects.filter(user=user).delete()
            TopicFollow.objects.filter(user=user).delete()
            for senator in request.POST.getlist('senators'):
                PersonFollow.objects.create(user=user, person_id=senator)
            for representative in request.POST.getlist('representatives'):
                PersonFollow.objects.create(user=user, person_id=representative)
            for location in request.POST.getlist('locations'):
                LocationFollow.objects.create(user=user, location=location)
            for subject in request.POST.getlist('subjects'):
                TopicFollow.objects.create(user=user, topic=subject)
        return redirect('.')

    prefernces = get_object_or_404(Preferences, user=user) or Preferences.objects.create(user=user)

    address = prefernces.address
    address_senator_name = None
    address_senator_url = None
    address_representative_name = None
    address_representative_url = None
    error_message = None

    if request.session.get('error_message'):
        error_message = request.session['error_message']

    if request.session.get('senator'):
        address_representative_name = request.session['representative']['name']
        address_representative_url = request.session['representative']['url']

        address_senator_name = request.session['senator']['name']
        address_senator_url = request.session['senator']['url']

    return render(
        request,
        'preferences/preferences.html',
        {
            'user': user,
            'senators': selected_senators,
            'representatives': selected_reps,
            'locations': selected_locations,
            'subjects': selected_subjects,
            'address': address,
            'address_senator_name': address_senator_name,
            'address_senator_url': address_senator_url,
            'address_representative_url': address_representative_url,
            'address_representative_name': address_representative_name,
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
        preferences.lat = float(lat)
        preferences.lon = float(lon)
        preferences.address = address
        preferences.save()

        api_resp = requests.get(settings.DOMAIN + '/api/people/?latitude={}&longitude={}'.format(preferences.lat, preferences.lon)).json()
        if api_resp['count'] == 2:
            for person in api_resp['results']:
                if 'Senators' in person['image']:
                    address_senator_url = person['url']
                    address_senator_name = person['name']
                    request.session['senator'] = {'name': address_senator_name, 'url': address_senator_url}
                    senator_id = furl.furl(person['url']).pathstr.replace('/api/', '')[:-1]
                    PersonFollow.objects.create(user=user, person_id=senator_id)
                else:
                    address_representative_url = person['url']
                    address_representative_name = person['name']
                    request.session['representative'] = {'name': address_representative_name, 'url': address_representative_url}
                    representative_id = furl.furl(person['url']).pathstr.replace('/api/', '')[:-1]
                    PersonFollow.objects.create(user=user, person_id=representative_id)
            request.session['error_message'] = None
        else:
            request.session['error_message'] = 'No matching Senators or representatives for the address entered, be sure to enter a valid FL address'
    return redirect('../preferences/')
