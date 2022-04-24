from utils import *


class BBS:
    def __init__(self, p: int = 687444379, q: int = 419074319, seed: int = 6367859):
        print('BBS class has been initialized')
        self.__p: int = p
        self.__q: int = q
        self.seed: int = seed

        self.blum_integer: int = self.__p * self.__q

        print(self.__str__())

    def __str__(self):
        return f'BBS p={self.__p} q={self.__q} seed={self.seed}'

    def generate_bytes(self, length: int) -> bytes:
        seed, length = self.seed, length * 8

        numbers = ''
        for _ in range(length):
            seed = seed ** 2 % self.blum_integer
            numbers += str(seed % 2)

        key = ''
        segments = [numbers[i:i + 8] for i in range(0, len(numbers), 8)]
        for s in segments:
            key += chr(int(s, 2))

        return str_to_bytes(key)
