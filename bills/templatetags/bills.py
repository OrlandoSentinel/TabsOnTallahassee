from django import template

register = template.Library()

@register.filter
def force_https(value):
    return value.replace('http://', 'https://')
