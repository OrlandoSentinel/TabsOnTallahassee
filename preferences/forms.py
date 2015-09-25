from django import forms
from registration.forms import RegistrationFormUniqueEmail

from preferences.models import Preferences

from opencivicdata.models.people_orgs import Person


class CustomModelFilter(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % (obj.name)

class PreferencesForm(forms.ModelForm):
    senator = CustomModelFilter(queryset=Person.objects.filter(memberships__organization__name='Florida Senate'))

    class Meta:
        model = Preferences
        fields = ['street_line1', 'street_line2', 'zipcode', 'city', 'state']
