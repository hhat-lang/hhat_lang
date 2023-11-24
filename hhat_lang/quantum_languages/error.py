"""Custom handling errors classes for quantum language packages"""


class NoQuantumLanguageError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidQuantumLanguageError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
