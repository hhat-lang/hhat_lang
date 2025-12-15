from __future__ import annotations

import sys
from enum import IntEnum, auto
from typing import Hashable


class InstrStatus(IntEnum):
    """
    Instruction status. To be used for asynchronous operations.
    """

    NOT_STARTED = auto()
    RUNNING = auto()
    TIMEOUT = auto()
    INTERRUPTED = auto()
    DONE = auto()
    ERROR = auto()


#######################################
# PERFECT HASH FUNCTION (PHF) SECTION #
#######################################


def get_phf_prime(tuple_len: int) -> int:
    """
    Retrieve a prime for the perfect hash function (PHF) algorithm. Use the tuple length
    to check which primer number to use, which must be bigger than ``tuple_len``.

    Probably a relatively good size project may have a few hundreds items (types and
    functions combined). By that time, python will not be useful to interpret the code
    anyway, but we never know what things will come out of it.
    """

    if tuple_len <= 2**5:
        return 37

    if tuple_len <= 2**6:
        return 67

    if tuple_len <= 2**8:
        return 257

    if tuple_len <= 2**12:
        return 4_099

    if tuple_len <= 2**14:
        return 16_411

    # I don't think this number below will ever be needed, but for future references
    return 1_048_583


PHF_A_LIMIT = 1_000_000
"""perfect hash function (PHF) parameter ``a`` limit"""

# only compatible with 64- or 128-bit systems
PHF_R_LIMIT = 127 if sys.maxsize > 2**64 else 61
"""perfect hash function (PHF) parameter ``r`` limit"""


class ResultPHF:
    """Hold PHF result values"""

    _a: int
    _r: int
    _n: int
    _prime: int
    __slots__ = ("_a", "_r", "_n", "_prime")

    def __init__(self, *, a: int, r: int, prime: int, n: int):
        self._a = a
        self._r = r
        self._prime = prime
        self._n = n

    @property
    def a(self) -> int:
        return self._a

    @property
    def r(self) -> int:
        return self._r

    @property
    def n(self) -> int:
        return self._n

    @property
    def prime(self) -> int:
        return self._prime

    def __repr__(self) -> str:
        return f"PHF(a={self.a}, r={self.r}, prime={self.prime}, n={self.n})"


def get_hash_with_args(value: int, a: int, r: int, n: int, prime: int) -> int:
    """
    Calculate the hash without a ``ResultPHF`` instance, but with the args. Use it when
    finding the correct args to produce the PHF values (``a`` and ``r``) combination.
    """

    p = value * a
    return ((p ^ (p >> r)) % prime) % n


def _gen_res_a_r_phf(
    group_tuple: tuple[Hashable, ...],
    tuple_len: int,
    a: int,
    r: int,
    prime: int,
) -> tuple[Hashable, ...]:
    """
    Generate a perfect hash function (PHF) tuple.

    Args:
        group_tuple: the tuple of IR hashes, or IR hashes and symbol/function check tuple-pairs
        tuple_len:
        a: an integer parameter to define the index for each element in the ``group_tuple``
        r: another integer parameter to define the index for each element in the ``group_tuple``
        prime: the prime number used to define the index for each element in the ``group_tuple``

    Returns:
        A tuple with the ``group_tuple`` ordered by their PHF index. Empty tuple if the PHF
        could not be found.
    """

    collision: bool = False
    res_list: list = [None for _ in range(tuple_len)]

    for obj in group_tuple:
        h = get_hash_with_args(hash(obj), a, r, tuple_len, prime)

        if obj not in res_list and res_list[h] is None:
            res_list[h] = obj

        else:
            collision = True
            break

    if not collision and None not in res_list:
        return tuple(res_list)

    return ()


def gen_phf(
    group_tuple: tuple[Hashable, ...],
) -> tuple[tuple[Hashable, ...], ResultPHF]:
    """
    Generate the perfect hash function (PHF). Each ``group_tuple`` element will be ordered
    in a new tuple according to its newly calculated hash value. Each element has exactly
    one unique index number that wil define its position in the new tuple.

    Args:
        group_tuple: a tuple with IR hash elements, or IR hash and symbol/function
            check tuple-pairs

    Returns:
        A resulting tuple with the elements positioned in their respective index number
        inside the tuple, and a ``ResultPHF`` instance with the ``a`` and ``r`` parameters
        to retrieve the hash values of each element.
    """

    tuple_len: int = len(group_tuple)
    prime = get_phf_prime(tuple_len)

    for a in range(1, PHF_A_LIMIT):
        for r in range(PHF_R_LIMIT):
            res_list = _gen_res_a_r_phf(group_tuple, tuple_len, a, r, prime)

            if res_list:
                return tuple(res_list), ResultPHF(a=a, r=r, prime=prime, n=tuple_len)

    raise ValueError("could not find satisfactory parameter values to generate the PHF")


def get_hash(value: int, phf: ResultPHF) -> int:
    """Retrieve a number given a value hash (``value``) and a phf instance (``ResultPHF``)"""

    p = value * phf.a
    return ((p ^ (p >> phf.r)) % phf.prime) % phf.n
