

from opencivicdata.models.people_orgs import Person


def get_current_people(position):

    if position == 'senator':
        return Person.objects.filter(memberships__organization__name='Florida Senate')
    if position == 'representative':
        return Person.objects.filter(memberships__organization__name='Florida House of Representatives')
