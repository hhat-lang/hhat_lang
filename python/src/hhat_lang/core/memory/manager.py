from __future__ import annotations

from collections import deque
from queue import LifoQueue
from typing import Any

from hhat_lang.core.memory.data_manager import DataReference


class MemoryManager:
    heap: DataReference
    stack: LifoQueue

    def __init__(self):
        self.heap = DataReference()
        self.stack = LifoQueue()


