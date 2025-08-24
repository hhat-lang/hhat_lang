from __future__ import annotations

from typing import Any

from hhat_lang.dialects.heather.code.simple_ir_builder.new_ir import IRBlock


class Evaluator:
    def __init__(self, code: IRBlock):
        if isinstance(code, IRBlock):
            self._code = code

        else:
            raise ValueError("code to be evaluated must be an IR type.")

    def walk(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def run(self):
        pass
