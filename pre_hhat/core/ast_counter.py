class Counter:
    count = 0

    def __init__(self):
        self.add_count()

    @classmethod
    def add_count(cls):
        cls.count += 1
