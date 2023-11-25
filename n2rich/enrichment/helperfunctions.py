import re
import json
import os

def string_parser(string: str) -> list:
    if type(string) != str:
        return None
    string = string.upper()
    return re.findall(r'([^ ,\t\n\r\f]+)', string)

def get_selected_field_dbs(field) -> list:

    all_fields = open('./staticfiles/json/fields.json')
    all_fields_loaded = json.load(all_fields)

    selected_field = all_fields_loaded.get(field, None)

    return selected_field

def replacedb(value:str, arg):
    parsed_value = value.split(arg)
    if not parsed_value[-1].isdigit():
        return value.replace(arg, " ")
    return " ".join(parsed_value[:-1])

def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def get_upload_path(instance, filename):
    return os.path.join("{}/{}/{}".format(instance.analysed_at.year, instance.analysed_at.month, instance.analysed_at.day), filename)