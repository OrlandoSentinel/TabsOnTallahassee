from django import forms
from registration.forms import RegistrationFormUniqueEmail

from preferences.models import Preferences

# from django.forms import ModelForm

# class RegistrationUserForm(RegistrationFormUniqueEmail):

#     class Meta:
#         model = User
#         fields = ("email")


class PreferencesForm(forms.ModelForm):
    class Meta:
        model = Preferences
        fields = ['representitive', 'senator', 'street_line1', 'street_line2',
                  'zipcode', 'city', 'state']
