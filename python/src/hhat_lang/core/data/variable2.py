from __future__ import annotations

from typing import Any

from hhat_lang.core.data.core import Symbol, CompositeSymbol
from hhat_lang.core.data.utils import AbstractDataContainer
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure


class DataCollection:
    pass


class DataContainer(AbstractDataContainer):
    """
    Data container for constant, variable and temporary data definitions.
    """

    _name: Symbol | CompositeSymbol
    _type: BaseTypeDataStructure
    _data: DataCollection
