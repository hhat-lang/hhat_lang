"""Custom handling error classes for quantum backends"""


class NoQuantumBackendError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidQuantumBackendError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
