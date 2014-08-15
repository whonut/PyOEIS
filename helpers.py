from itertools import chain
from operator import methodcaller


def parse_comma_separated(l):
    split = map(methodcaller('split', ','), l)
    flat = chain.from_iterable(split)
    return [int(s) for s in flat if s != '']
