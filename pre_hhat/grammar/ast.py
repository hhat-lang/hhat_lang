"""AST"""


class AST:
    def __init__(self, name, *value):
        self.value = value
        self.name = name

    def __iter__(self):
        yield from self.value

    def __hash__(self):
        return hash((self.name, self.value))

    def __len__(self):
        return len(self.value)

    def __eq__(self, other):
        if isinstance(other, AST):
            if self.name == other.name:
                if len(self) == len(other):
                    for s, o in zip(self, other):
                        if s != o:
                            return False
                    return True
            return False
        if isinstance(other, str):
            if self.name == other:
                return True
            return False
        return False

    def __repr__(self):
        values = ", ".join([str(k) for k in self])
        return f"{self.name}({values})"
