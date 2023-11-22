from django import template

register = template.Library()

@register.filter
def username_first(value:str, arg):
    username = value.email
    parsed_username = username.split(arg)
    return parsed_username[0]