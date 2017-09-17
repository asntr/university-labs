class Hasher:
    MAX_VALUE = 18446744073709551616

    PRIME = 307

    def __init__(self, text):
        self.powers = self.__precalculate_powers(len(text))
        self.hashes = self.__precalculate_prefix_hashes(text, self.powers)

    def __len__(self):
        return len(self.hashes)

    def __getitem__(self, item):
        if isinstance(item, slice):
            stop = item.stop if item.stop else len(self.hashes)
            if item.start:
                return self.hashes[stop - 1] - self.hashes[item.start - 1], self.powers[item.start]
            else:
                return self.hashes[item.stop - 1], 1
        else:
            return self.hashes[item], 1

    @classmethod
    def __precalculate_powers(cls, n):
        powers = [None] * (n+1)
        powers[0] = 1
        for i in range(1, n+1):
            next_power = (powers[i-1] * cls.PRIME % cls.MAX_VALUE) + cls.MAX_VALUE
            powers[i] = next_power % cls.MAX_VALUE
        return powers

    @classmethod
    def __precalculate_prefix_hashes(cls, text, powers):
        n = len(text)
        hashes = [None] * n
        hashes[0] = ord(text[0])
        for i in range(1, n):
            next_hash = cls.MAX_VALUE + (hashes[i-1] + powers[i] * ord(text[i])) % cls.MAX_VALUE
            hashes[i] = next_hash % cls.MAX_VALUE
        return hashes
