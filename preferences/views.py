from django.shortcuts import render
from django.db import transaction
# from django.views.generic import TemplateView

from tot.utils import get_current_people

from bills.utils import get_all_subjects, get_all_locations

from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView

from preferences.models import PersonFollow

from opencivicdata.models.people_orgs import Person



class EmailRegistrationView(RegistrationView):

    form_class = RegistrationFormUniqueEmail


def user_preferences(request):
    user = request.user

    senators = get_current_people(position='senator')
    representatives = get_current_people(position='representative')

    locations = get_all_locations()
    subjects = get_all_subjects()

    if request.method == 'POST':
        with transaction.atomic():
            PersonFollow.objects.filter(user=user).delete()
            for senator in request.POST.getlist('senators'):
                PersonFollow.objects.create(user=user, person_id=senator)
            for representative in request.POST.getlist('representatives'):
                PersonFollow.objects.create(user=user, person_id=representitive)
            for location in request.POST.getlist('locations'):
                PersonFollow.objects.create(user=user, person_id=representitive)
            for subject in request.POST.getlist('subjects'):
                PersonFollow.objects.create(user=user, person_id=representitive)

    return render(
        request,
        'preferences/preferences.html',
        {
            'user': user,
            'senators': senators,
            'representatives': representatives,
            'locations': locations,
            'subjects': subjects
         }
    )