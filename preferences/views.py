from django.shortcuts import render
from django.views.generic.edit import FormView

from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView

from preferences.forms import PreferencesForm


class EmailRegistrationView(RegistrationView):

    form_class = RegistrationFormUniqueEmail


class UserPreferences(FormView):
    template_name = 'preferences/preferences.html'
    form_class = PreferencesForm
    success_url = '/index/'

    def form_valid(self, form):
        return super(UserPreferences, self).form_valid(form)