from rest_framework import filters
from rest_framework.serializers import ValidationError

from .jsonapi import group_query_params_by_family


def extract_filter_expressions(query_dict, serializer) -> dict[str, str]:
    """Extract the "filter" family of expressions from the query dict and format them for use.

    Since no formal JSON:API scheme exists for complex filter operations, we have settled on the following norm:
    Filter params can have either one or two arguments.
    The first argument MUST be a field on the serialized output of the endpoint
    The second arugment is an OPTIONAL comparison operator (i.e. `icontains`, `lte`, etc.)
    """
    filter_params = group_query_params_by_family(query_dict.lists()).get("filter", [])
    return {
        _format_filter_args(param.args, serializer): param.value
        for param in filter_params
    }


def _format_filter_args(query_args, serializer):
    """Parse and format the query args into a kwarg key suitable for Django filtering."""
    try:
        field = serializer.fields[query_args[0]].source
    except (IndexError, KeyError):
        raise ValidationError(
            "Filter query parameters must specify a field to filter on"
        )

    match len(query_args):
        case 1:
            operation = None
        case 2:
            operation = query_args[1]
        case _:
            raise ValidationError(
                "Filter query parameters only accept one field and one (optional) comparison operator"
            )

    return field if operation is None else f"{field}__{operation}"


class AddonServiceFilteringBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_expressions = extract_filter_expressions(
            request.query_params, view.get_serializer()
        )
        return queryset.filter(**filter_expressions)


class RestrictedListEndpointFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        required_filters = set(view.required_list_filter_fields)
        filter_expressions = extract_filter_expressions(
            request.query_params, view.get_serializer()
        )
        missing_filters = required_filters - filter_expressions.keys()
        if missing_filters:
            raise ValidationError(
                f"Request was missing the following required filters for this endpoint: {missing_filters}"
            )
        return queryset.filter(**filter_expressions)
