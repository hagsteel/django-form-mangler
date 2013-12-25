from django import template

register = template.Library()


@register.filter(name='stringify')
def stringify(value):
    return str(value)
