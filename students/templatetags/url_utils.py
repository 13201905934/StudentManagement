from django import template
from django.http import QueryDict

from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def search_url(request, **kwargs):
    query_params = QueryDict(request.META['QUERY_STRING'], mutable=True)
    for key, value in kwargs.items():
        if value is None:
            query_params.pop(key, None)
        else:
            query_params.setlist(key, [value])
    return urlencode(query_params, doseq=True)

