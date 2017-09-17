class ShiftableString(str):
    def __lshift__(self, other):
        other = other % len(self)
        return self[other:] + self[:other]

    def __rshift__(self, other):
        other = other % len(self)
        return self[-other:] + self[:-other]
