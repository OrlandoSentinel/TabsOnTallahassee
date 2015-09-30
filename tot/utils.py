

from opencivicdata.models.people_orgs import Person, Organization


def get_current_people(position):

    if position == 'senator':
        return Organization.objects.get(name='Florida Senate').get_current_members()
    if position == 'representative':
        return Organization.objects.get(name='Florida House of Representatives').get_current_members()


def mark_selected(items, items_followed):
    selected_items = []
    for item in items:
        item_dict = {}
        item_dict['item'] = item
        if item in items_followed:
            item_dict['selected'] = True
        else:
            item_dict['selected'] = False
        selected_items.append(item_dict)

    return selected_items
