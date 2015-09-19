from registration.forms import RegistrationFormUniqueEmail

class RegistrationUserForm(RegistrationFormUniqueEmail):

    class Meta:
        model = User
        fields = ("email")
