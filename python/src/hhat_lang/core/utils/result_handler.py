from __future__ import annotations

from enum import StrEnum
from typing import Any


class ResultType(StrEnum):
    OK = "ok"
    ERROR = "error"


class Result:
    def __init__(self, result_type: ResultType):
        self.type: ResultType = result_type
        self.result: Any | None = None

    @property
    def value(self) -> Any:
        return self.result

    def __call__(self, result: Any) -> Result:
        match self.type:
            case ResultType.OK:
                self.result = result
                return self
            case ResultType.ERROR:
                self.result = result or None
                return self

    def __bool__(self) -> bool:
        return self.type is not ResultType.ERROR
