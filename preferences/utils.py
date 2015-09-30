
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
