from django import forms
from registration.forms import RegistrationFormUniqueEmail

from preferences.models import Preferences

from opencivicdata.models.people_orgs import Person


# from django.forms import ModelForm

# class RegistrationUserForm(RegistrationFormUniqueEmail):

#     class Meta:
#         model = User
#         fields = ("email")


# class PreferencesForm(forms.ModelForm):
#     class Meta:
#         model = Preferences
#         fields = ['representitive', 'senator', 'street_line1', 'street_line2',
#                   'zipcode', 'city', 'state']

#         def __init__(self, **kwargs):
#                 super(PreferencesForm, self).__init__(**kwargs)
#                 self.fields['senator'].queryset = Preferences.objects.filter(memberships='Florida: Florida Senate')


class CustomModelFilter(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # import ipdb; ipdb.set_trace()
        return "%s" % (obj.name)

class PreferencesForm(forms.ModelForm):
    senator = CustomModelFilter(queryset=Person.objects.filter(name='Aaron Bean'))

    class Meta:
        model = Preferences
        fields = ['representitive', 'senator', 'street_line1', 'street_line2',
                  'zipcode', 'city', 'state']