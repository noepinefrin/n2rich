from django import template

register = template.Library()

@register.filter
def replacedb(value:str, arg):
    parsed_value = value.split(arg)
    if not parsed_value[-1].isdigit():
        return value.replace(arg, " ")
    return " ".join(parsed_value[:-1])


