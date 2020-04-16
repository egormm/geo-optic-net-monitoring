import functools
from string import ascii_uppercase
from typing import Iterable

POSITIVE_VALUES = ('true', '1', 'yes')
ALPHABET = ascii_uppercase
MOVED_ALPHABET = ALPHABET[-1] + ALPHABET[:-1]


# using wonder's beautiful simplification: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects/31174427?noredirect=1#comment86638618_31174427
def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split('.'))


def int_to_bijective_hexavigesimal(n: int) -> str:
    base = len(ALPHABET)
    s = ALPHABET[n % base]
    while True:
        n //= base
        if n <= 0:
            return s[::-1]
        s += MOVED_ALPHABET[n % base]


def query_bool_to_py(bs: str) -> bool:
    return bs.lower() in POSITIVE_VALUES


def get_fields_list(klass: Iterable, field: str):
    if not isinstance(field, str):
        raise ValueError("Functions takes exactly one string argument")
    return [str(rgetattr(el, field)) for el in klass]
