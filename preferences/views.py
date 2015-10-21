from django.db import transaction
from django.shortcuts import render, redirect
from opencivicdata.models import Person, Organization
from bills.utils import get_all_subjects, get_all_locations
from preferences.models import PersonFollow, LocationFollow, TopicFollow
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

    if request.method == 'POST':
        with transaction.atomic():
            PersonFollow.objects.filter(user=user).delete()
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
            'subjects': selected_subjects
        }
    )
