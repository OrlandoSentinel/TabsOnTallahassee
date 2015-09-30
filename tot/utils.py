

from opencivicdata.models.people_orgs import Person, Organization


def get_current_people(position):
    if position == 'senator':
        return Organization.objects.get(name='Florida Senate').get_current_members()
    if position == 'representative':
        return Organization.objects.get(name='Florida House of Representatives').get_current_members()
