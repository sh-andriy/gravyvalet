import dataclasses
import re
from typing import (
    ClassVar,
    Iterable,
    Pattern,
)


@dataclasses.dataclass(frozen=True)
class JSONAPIQueryParam:
    """Dataclass for describing the contents of a JSON:API-compliant Query Parameter."""

    family: str
    members: tuple[str] = ()  # Term "member" borrowed from jsonapi.net
    values: tuple[str] = ()

    # Matches any alphanumeric string followed by an open bracket or end of input
    # (can include "_" or "-" if outside of the first or last position)
    # Note: [^\W_] is equivalent to [a-zA-Z0-9]
    FAMILY_REGEX: ClassVar[Pattern] = re.compile(r"^[^\W_]([\w-]*[^\W^])?(?=\[|$)")
    # Captures any text located within square brackets
    MEMBER_REGEX: ClassVar[Pattern] = re.compile(r"\[(?P<name>[^[\]]*)\]")

    @classmethod
    def from_key_value_pair(cls, query_param_name, query_param_values):
        family, members = cls.parse_param_name(query_param_name)
        if not isinstance(query_param_values, tuple):
            query_param_values = tuple(query_param_values)
        return cls(family, members, query_param_values)

    @classmethod
    def parse_param_name(cls, query_param_name: str) -> tuple[str, tuple[str]]:
        """Parses a query parameter name into its family and bracketed members.

        >>> JSONAPIQueryParam.parse_param_name('filter')
        ('filter, ())

        >>> JSONAPIQueryParam.parse_param_name('filter[field]')
        ('filter', ('field',)

        >>> JSONAPiQueryParam.parse_param_name('filter[nested][field]')
        ('filter', ('nested', 'field'))
        """
        if not cls._param_name_is_valid(query_param_name):
            raise ValueError(f"Invalid query param name: {query_param_name}")
        family_match = cls.FAMILY_REGEX.match(query_param_name)
        family = family_match.group()
        member_slice_start = (
            family_match.end()
        )  # precommits got very confused when this was inlined
        members = cls.MEMBER_REGEX.findall(query_param_name[member_slice_start:])
        return (family, tuple(members))

    @classmethod
    def _param_name_is_valid(cls, query_param_name: str) -> bool:
        """Validates that a given query parameter has a valid name in JSON:API.

        >>> JSONAPIQueryParam._param_name_is_valid('filter')
        True

        >>> JSONAPIQueryPAram._param_name_is_valid('filter[so][many][nested][fields]')
        True

        >>> JSONAPiQueryParam._param_name_is_valid('_filter')
        False

        >>> JSONAPIQueryParam._param_name_is_valid('fi&lter')
        False

        >>> JSONAPIQueryParam._param_name_is_valid('filter[field')
        False

        >>> JSONAPIQueryParam._param_name_is_valid('filter[field]extra')
        False
        """
        full_match_regex = re.compile(
            f"{cls.FAMILY_REGEX.pattern}({cls.MEMBER_REGEX.pattern})*$"
        )
        if not full_match_regex.match(query_param_name):
            return False
        return True

    def __str__(self):
        bracketed_members = "".join([f"[{member}]" for member in self.members])
        values = ",".join([str(value) for value in self.values])
        return f"{self.family}{bracketed_members}={values}"


QueryParamFamilies = dict[
    str, Iterable[JSONAPIQueryParam]  # keyed by query_param family
]


def group_query_params_by_family(
    query_items: Iterable[tuple[str, Iterable[str]]]
) -> QueryParamFamilies:
    """Extracts JSON:API query familes from a list of (ParameterName, ParameterValues) tuples.

    Data should be pre-normalized before calling, such as by using the results of
    `urllib.parse.parse_qs(...).items()` or `django.utils.QueryDict.lists()`
    """
    grouped_query_params = QueryParamFamilies()
    for _unparsed_name, _param_values in query_items:
        parsed_query_param = JSONAPIQueryParam.from_key_value_pair(
            _unparsed_name, _param_values
        )
        grouped_query_params.setdefault(parsed_query_param.family, []).append(
            parsed_query_param
        )
    return grouped_query_params


def extract_filter_expressions(query_dict) -> dict[str, str]:
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
    return {"__".join(param.members): ",".join(param.values) for param in filter_params}
