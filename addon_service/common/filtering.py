from rest_framework import filters
from rest_framework.serializers import ValidationError

from .jsonapi import group_query_params_by_family


def extract_filter_expressions(query_dict, serializer) -> dict[str, str]:
    """Extract the "filter" family of expressions from the query dict and format them for use.

    Since no formal JSON:API scheme exists for complex filter operations, we will
    Assumes that nested brackets are used to represent the equivalent of a `__` in Django,
    i.e. a nested lookup or a named, non-equality comparison operation.

    For example:
    addons.osf.io/v1/user_references/{key}/authorized_storage_accounts/?filter=[created][lt]=YYYYYMMDD
    would return only the authorized storage accounts for a given user that are older than the provided date

    Similarly
    /v1/resource_references/{key}/configured_storage_addons/?filter[base_account][external_strorage_service][name]=GoogleDrive
    would return just the Google Drive addons for a given resource.
    """
    filter_params = group_query_params_by_family(query_dict.lists()).get("filter", [])
    return {
        _format_filter_expression(param.args, serializer): param.value
        for param in filter_params
    }


def _format_filter_expression(query_args, serializer):
    operation = None
    field = serializer.fields[query_args[0]].source
    if len(query_args) == 2:
        operation = query_args[1]
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
