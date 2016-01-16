from django import template

register = template.Library()


@register.filter
def name_swap(value):
    # special case for this name
    if value == 'Braynon, Oscar II':
        return 'Oscar Braynon II'

    pieces = value.split(', ')

    if len(pieces) == 2:
        # reverse name in place
        return ' '.join(pieces[::-1])
    elif len(pieces) == 3:
        titles = ('Jr.', 'Sr.')
        name_pieces = []
        title_pieces = []
        for p in pieces:
            if p in titles:
                title_pieces.append(p)
            else:
                name_pieces.append(p)
        if len(name_pieces) == 2:
            return ' '.join(name_pieces[::-1] + title_pieces)
    # always fallback to something
    return value
