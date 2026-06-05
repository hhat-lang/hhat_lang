from __future__ import annotations

from collections import deque

from hhat_lang.core.data.core import Symbol
from hhat_lang.core.error_handlers.errors import IndexAllocationError
from hhat_lang.core.memory.core import IndexManager


def test_index_request_smaller() -> None:
    q = Symbol("@q")

    im1 = IndexManager(7)
    im1.add(q, 5)

    assert isinstance(im1.request(q), deque)
    assert im1.resources[q] == 5
    assert len(im1._available) == 2
    assert len(im1._allocated) == 5
    assert im1._in_use_by.get(q, False) is not False
    assert im1._in_use_by[q][0] == 0

    im1.free(q)

    assert len(im1._available) == 7
    assert len(im1._allocated) == 0

    assert im1._in_use_by.get(q, False) is False


def test_index_request_larger() -> None:
    q = Symbol("@q")

    im1 = IndexManager(7)

    assert isinstance(im1.add(q, 9), IndexAllocationError)


def test_index_request_eq() -> None:
    q = Symbol("@q")

    im1 = IndexManager(7)
    im1.add(q, 7)

    assert isinstance(im1.request(q), deque)
    assert len(im1._available) == 0
    assert len(im1._allocated) == 7
    assert im1._in_use_by.get(q, False) is not False
