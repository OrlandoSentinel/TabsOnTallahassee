from django.db import transaction
from django.shortcuts import render

from opencivicdata.models.people_orgs import Person

from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView
from tot.utils import get_current_people
from bills.utils import get_all_subjects, get_all_locations
from preferences.utils import mark_selected
from preferences.models import PersonFollow, LocationFollow, TopicFollow


class EmailRegistrationView(RegistrationView):
    form_class = RegistrationFormUniqueEmail


def user_preferences(request):
    user = request.user

    senators = get_current_people(position='senator')
    representatives = get_current_people(position='representative')
    locations = get_all_locations()
    subjects = get_all_subjects()

    people_followed = [individual.person for individual in PersonFollow.objects.filter(user=user)]
    subjects_followed = [subject.topic for subject in TopicFollow.objects.filter(user=user)]
    locations_followed = [location.location for location in LocationFollow.objects.filter(user=user)]

    selected_reps = mark_selected(representatives, people_followed)
    selected_senators = mark_selected(senators, people_followed)
    selected_subjects = mark_selected(subjects, subjects_followed)
    selected_locations = mark_selected(locations, locations_followed)

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