from encryptor import Encryptor
from hasher import Hasher
from vigenere_hacker import VigenereHacker, kasiski_method


def main():
    with open('vigenere_and_kasiski/rus_text.txt', 'r') as test:
        text = test.read()
    encryptor = Encryptor("абвг", lang='rus')
    encrypted = encryptor.encrypt(text)
    print("encrypted: ", encrypted)
    hasher = Hasher(encrypted)
    lengths = kasiski_method(hasher, 3)
    hacker = VigenereHacker('rus')
    for length, _ in filter(lambda x: 3 < x[0] < len(encrypted) // 2, lengths.most_common(5)):
        for decrypted in hacker.hack(encrypted, length):
            if decrypted == text:
                print("code word length = {}".format(length))
                print("decrypted: ", decrypted)
                return

if __name__ == '__main__':
    main()
