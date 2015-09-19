from django.shortcuts import render

# Create your views here.

from registration.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail

class EmailRegistrationView(RegistrationView):

    form_class = RegistrationFormUniqueEmail