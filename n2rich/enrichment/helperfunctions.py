import re
import json

def string_parser(string: str) -> list:
    if type(string) != str:
        return None
    return re.findall(r'([^ ,\t\n\r\f]+)', string)

def get_selected_field_dbs(request) -> list:

    all_fields = open('./staticfiles/json/fields.json')
    all_fields_loaded = json.load(all_fields)

    selected_field = all_fields_loaded[request.POST.get('enrichment_field')]

    return selected_field