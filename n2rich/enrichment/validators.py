from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .helperfunctions import string_parser

def gene_list_validator(gene_list: str) -> bool | None:
    gl = string_parser(gene_list)

    if len(gl) > 100 or len(gl) == 1:
        raise ValidationError(
            _("%(value)s Gene list must between 1 < gene_list <= 100"),
            params={"value": gene_list},
        )
