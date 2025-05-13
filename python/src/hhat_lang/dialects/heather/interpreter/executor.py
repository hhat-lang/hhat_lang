from __future__ import annotations

from typing import Any

from hhat_lang.core.code.ir import BaseIR


class Evaluator:
    def __init__(self, code: BaseIR):
        if isinstance(code, BaseIR):
            self._code = code

        else:
            raise ValueError("code to be evaluated must be an IR type.")

    def walk(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def run(self):
        pass
