from itertools import chain
from operator import methodcaller


def parse_comma_separated_findall(l):
    '''Returns a flat list of all elements in l that are separated by
       a comma or end-of-list'''
    split = map(methodcaller('split', ','), l)
    flat = chain.from_iterable(split)
    return [s for s in flat if s != '']
