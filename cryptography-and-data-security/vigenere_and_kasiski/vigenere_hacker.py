from collections import Counter
from collections import defaultdict
from functools import reduce
import operator
from itertools import combinations, product


from shiftable_string import ShiftableString


def factors_of(x):
    return [i for i in range(2, x // 2 + 1) if x % i == 0] + [x]


def kasiski_method(hasher, l):
    counter = defaultdict(list)
    for start in range(len(hasher) - l + 1):
        substring_hash, _ = hasher[start:start+l]  # hash is multiplied by p^start
        absolute_hash = (substring_hash * hasher.powers[len(hasher) - start] + hasher.MAX_VALUE) % hasher.MAX_VALUE
        counter[absolute_hash].append(start)
    factors = reduce(
        operator.add, map(
            lambda x: reduce(operator.add, [factors_of(j-i) for i, j in combinations(x, 2)] or [[1]]), counter.values()
        )
    )
    return Counter(factors)


class VigenereHacker:

    FREQ_MISTAKE = 0.15

    alphabets = {
        'rus': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
        'eng': 'abcdefghijklmnopqrstuvwxyz',
    }

    frequencies = {
        'eng': {
            'a': 0.08167,
            'b': 0.01492,
            'c': 0.02782,
            'd': 0.04253,
            'e': 0.12702,
            'f': 0.0228,
            'g': 0.02015,
            'h': 0.06094,
            'i': 0.06966,
            'j': 0.00153,
            'k': 0.00772,
            'l': 0.04025,
            'm': 0.02406,
            'n': 0.06749,
            'o': 0.07507,
            'p': 0.01929,
            'q': 0.00095,
            'r': 0.05987,
            's': 0.06327,
            't': 0.09056,
            'u': 0.02758,
            'v': 0.00978,
            'w': 0.0236,
            'x': 0.0015,
            'y': 0.01974,
            'z': 0.00074,
        },
        'rus': {
            'а': 0.07821,
            'б': 0.01732,
            'в': 0.04491,
            'г': 0.01698,
            'д': 0.03103,
            'е': 0.08567,
            'ж': 0.01082,
            'з': 0.01647,
            'и': 0.06777,
            'й': 0.01041,
            'к': 0.03215,
            'л': 0.04813,
            'м': 0.03139,
            'н': 0.0685,
            'о': 0.11394,
            'п': 0.02754,
            'р': 0.04234,
            'с': 0.05382,
            'т': 0.06443,
            'у': 0.02882,
            'ф': 0.00132,
            'х': 0.00833,
            'ц': 0.00333,
            'ч': 0.01645,
            'ш': 0.00775,
            'щ': 0.00331,
            'ъ': 0.00023,
            'ы': 0.01854,
            'ь': 0.02106,
            'э': 0.0031,
            'ю': 0.00544,
            'я': 0.01979,
            'ё': 0.01979,
        }
    }

    def __init__(self, lang='eng'):
        self.frequency = VigenereHacker.frequencies[lang]
        self.alphabet = VigenereHacker.alphabets[lang]

    def hack_string_by_frequency_analysis(self, s):
        letters_counts = Counter(filter(lambda ch: ch.isalpha(), s.lower()))
        total = sum(letters_counts.values())
        frequencies = {ch: float(letters_counts[ch]) / (total or 1) for ch in self.alphabet}
        shifted_alphabets = self.__match_by_frequency(frequencies)
        for alphabet in shifted_alphabets:
            yield ''.join([self.__decrypt_character(alphabet, ch) for ch in s])

    def hack(self, text, code_word_length):
        divisions = [text[i::code_word_length] for i in range(code_word_length)]
        generators = map(self.hack_string_by_frequency_analysis, divisions)
        for iterator in product(*generators):
            result = [None] * len(text)
            for i, string in enumerate(iterator):
                result[i::code_word_length] = string
            yield ''.join(result)

    def __decrypt_character(self, shifted_alphabet, ch):
        if not ch.isalpha():
            return ch
        upper = ch.isupper()
        index = shifted_alphabet.index(ch.lower())
        res = self.alphabet[index]
        return res.capitalize() if upper else res

    def __match_by_frequency(self, frequency):
        shifts = sorted(
            [(i, sum(
                [abs(frequency[s] - self.frequency[o]) for o, s in zip(self.alphabet, ShiftableString(self.alphabet) << i)]
            )) for i in range(len(self.alphabet))],
            key=lambda item: item[1],
        )
        for shift in filter(lambda x: x[1] - shifts[0][1] < self.FREQ_MISTAKE, shifts):
            yield ShiftableString(self.alphabet) << shift[0]
