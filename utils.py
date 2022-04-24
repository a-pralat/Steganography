from typing import BinaryIO, Tuple, Union, Optional, Match
from PyQt5 import uic, QtWidgets
from os.path import exists
from PIL.Image import Image
from PIL import Image
from math import ceil
import numpy as np
import sys
import re


def valid_seed(seed: str) -> bool:
    return bool(re.match('^\d{7}$', seed))


def valid_lsb_number(lsb_number: str) -> bool:
    return bool(re.match('^[1-8]{1}$', lsb_number))


def byte_xor(a: any, b: any) -> bytes:
    return bytes([x ^ y for (x, y) in zip(a, b)])


byte_depth_to_dtype = {1: np.uint8, 2: np.uint16, 4: np.uint32, 8: np.uint64}


def roundup(x: float, base: int = 1) -> int:
    return int(ceil(x / base)) * base


def max_bits_to_hide(image: Image, lsb_number: int) -> int:
    return int(3 * image.size[0] * image.size[1] * lsb_number)


def bytes_in_max_file_size(image: Image, lsb_number: int) -> int:
    return roundup(max_bits_to_hide(image, lsb_number).bit_length() / 8)


def str_to_bytes(x: any, charset: str = sys.getdefaultencoding(), errors: str = 'strict') -> any:
    if x is None:
        return None
    if isinstance(x, (bytes, bytearray, memoryview)):
        return bytes(x)
    if isinstance(x, str):
        return x.encode(charset, errors)
    if isinstance(x, int):
        return str(x).encode(charset, errors)
    raise TypeError("Expected bytes")


def lsb_interleave_bytes(carrier: any, payload: any, lsb_number: any, truncate: bool = False,
                         byte_depth: int = 1) -> bytes:
    plen = len(payload)
    payload_bits = np.zeros(shape=(plen, 8), dtype=np.uint8)
    payload_bits[:plen, :] = np.unpackbits(
        np.frombuffer(payload, dtype=np.uint8, count=plen)
    ).reshape(plen, 8)

    bit_height = roundup(plen * 8 / lsb_number)
    payload_bits.resize(bit_height * lsb_number)

    carrier_dtype = byte_depth_to_dtype[byte_depth]
    carrier_bits = np.unpackbits(
        np.frombuffer(carrier, dtype=carrier_dtype, count=bit_height).view(np.uint8)
    ).reshape(bit_height, 8 * byte_depth)

    carrier_bits[:, 8 * byte_depth - lsb_number: 8 * byte_depth] = payload_bits.reshape(
        bit_height, lsb_number
    )

    ret = np.packbits(carrier_bits).tobytes()
    return ret if truncate else ret + carrier[byte_depth * bit_height:]


def lsb_deinterleave_bytes(carrier: any, num_bits: int, lsb_number: int, byte_depth: int = 1) -> bytes:
    plen = roundup(num_bits / lsb_number)
    carrier_dtype = byte_depth_to_dtype[byte_depth]
    payload_bits = np.unpackbits(
        np.frombuffer(carrier, dtype=carrier_dtype, count=plen).view(np.uint8)
    ).reshape(plen, 8 * byte_depth)[:, 8 * byte_depth - lsb_number: 8 * byte_depth]
    return np.packbits(payload_bits).tobytes()[: num_bits // 8]


def lsb_interleave_list(carrier: any, payload: any, lsb_number: int) -> any:
    bit_height = roundup(8 * len(payload) / lsb_number)
    carrier_bytes = np.array(carrier[:bit_height], dtype=np.uint8).tobytes()
    interleaved = lsb_interleave_bytes(carrier_bytes, payload, lsb_number, truncate=True)
    carrier[:bit_height] = np.frombuffer(interleaved, dtype=np.uint8).tolist()
    return carrier


def lsb_deinterleave_list(carrier: any, num_bits: int, lsb_number: int):
    plen = roundup(num_bits / lsb_number)
    carrier_bytes = np.array(carrier[:plen], dtype=np.uint8).tobytes()
    deinterleaved = lsb_deinterleave_bytes(carrier_bytes, num_bits, lsb_number)
    return deinterleaved
