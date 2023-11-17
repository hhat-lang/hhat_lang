from __future__ import annotations
from typing import Any, Callable

from hhat_lang.quantum_languages.api import QASMAPI



class OpenQASM(QASMAPI):
    def parse_code(self, code: Any) -> Any:
        ...


