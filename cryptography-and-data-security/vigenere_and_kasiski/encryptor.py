from itertools import cycle

from shiftable_string import ShiftableString


class Encryptor:
    alphabets = {
        'rus': ShiftableString('абвгдеёжзийклмнопрстуфхцчшщъыьэюя'),
        'eng': ShiftableString('abcdefghijklmnopqrstuvwxyz'),
    }

    def __init__(self, code_word, lang='eng'):
        self.alphabet = Encryptor.alphabets[lang]
        self.lang = lang
        self.encrypting_table = []
        for letter in code_word:
            self.encrypting_table.append(self.alphabet << self.alphabet.index(letter))

    def encrypt(self, text):
        iterator = cycle(range(len(self.encrypting_table)))
        encrypted_text = ''.join([self.__encrypt_character(ch, next(iterator)) for ch in text])
        return encrypted_text

    def decrypt(self, text):
        iterator = cycle(range(len(self.encrypting_table)))
        decrypted_text = ''.join([self.__decrypt_character(ch, next(iterator)) for ch in text])
        return decrypted_text

    def __encrypt_character(self, ch, row):
        if not ch.isalpha():
            return ch
        upper = ch.isupper()
        index = self.alphabet.index(ch.lower())
        res = self.encrypting_table[row][index]
        return res.capitalize() if upper else res

    def __decrypt_character(self, ch, row):
        if not ch.isalpha():
            return ch
        upper = ch.isupper()
        index = self.encrypting_table[row].index(ch.lower())
        res = self.alphabet[index]
        return res.capitalize() if upper else res
