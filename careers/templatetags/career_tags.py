from django import template

from careers.catalog import class_rows

register = template.Library()


@register.simple_tag
def class_catalog():
    return class_rows()
