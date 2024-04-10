import operator
from functools import reduce

from . import (
    serializers,
    validators,
)


def combine_flags(member_list):
    return reduce(operator.__or__, member_list)


__all__ = (
    "combine_flags",
    "serializers",
    "validators",
)
