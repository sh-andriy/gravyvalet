import operator
from functools import reduce


def combine_flags(member_list):
    return reduce(operator.__or__, member_list)
