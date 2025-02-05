from __future__ import annotations

from typing import Any

from hhat_lang.core.quantum_lowlevel_api.base import BaseShotEstimator


class ShotsEstimator(BaseShotEstimator):
    def __init__(self, var_qsize: int, **options: Any):
        self._estimate_shots(var_qsize, **options)

    def _estimate_shots(self, var_qsize: int, **options: Any) -> None:
        # TODO: implement it later; for now, just a dumb calculation
        self.shots = var_qsize * 1_000 if var_qsize <= 12 else (var_qsize * 550 + 12_000)

    def __call__(self, **options: Any) -> int:
        return self.shots
