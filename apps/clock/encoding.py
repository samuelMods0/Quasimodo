# This file was written entirely by AI. Human-written replacements welcome.

"""Encode and decode the AllSync IQ Remote Connect 6-bit text format.

Each 6-bit value is represented by the ASCII character whose code point is
the value plus ``0x3C``.  This resembles Base64's bit packing, but it uses a
different alphabet and no padding character.
"""

from __future__ import annotations


_ENCODING_OFFSET = 0x3C
_SIX_BIT_MASK = 0x3F
_BYTE_MASK = 0xFF


def encode_bytes(data: bytes | bytearray | memoryview) -> str:
    """Return *data* in the AllSync IQ custom 6-bit encoding.

    The final 6-bit group is zero-padded on the right when the input does
    not end on a 6-bit boundary.  There is no explicit padding character.

    Args:
        data: Bytes to encode. ``bytearray`` and ``memoryview`` are accepted
            as other bytes-like inputs.

    Raises:
        TypeError: If *data* is not bytes-like.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("data must be bytes-like")

    # A memoryview may expose elements wider than one byte.  Normalizing it
    # here makes every supported input follow the same byte-oriented path.
    data = bytes(data)
    result: list[str] = []
    bit_buffer = 0
    bit_count = 0

    for byte in data:
        bit_buffer = (bit_buffer << 8) | byte
        bit_count += 8

        while bit_count >= 6:
            bit_count -= 6
            six_bit_value = (bit_buffer >> bit_count) & _SIX_BIT_MASK
            result.append(chr(six_bit_value + _ENCODING_OFFSET))
            bit_buffer &= (1 << bit_count) - 1

    if bit_count:
        six_bit_value = (bit_buffer << (6 - bit_count)) & _SIX_BIT_MASK
        result.append(chr(six_bit_value + _ENCODING_OFFSET))

    return "".join(result)


def decode_string(value: str) -> bytes:
    """Return bytes decoded from an AllSync IQ custom 6-bit string.

    Partial bytes at the end are discarded.  Canonically encoded values have
    zeroes in those positions because :func:`encode_bytes` right-pads its
    final group.

    Args:
        value: Text in the protocol's ASCII alphabet (``<`` through ``{``).

    Raises:
        TypeError: If *value* is not a string.
        ValueError: If *value* contains a character outside the encoding
            alphabet.
    """
    if not isinstance(value, str):
        raise TypeError("value must be a string")

    result = bytearray()
    bit_buffer = 0
    bit_count = 0

    for char in value:
        six_bit_value = ord(char) - _ENCODING_OFFSET
        if not 0 <= six_bit_value <= _SIX_BIT_MASK:
            raise ValueError(
                f"invalid encoded character {char!r} "
                f"(code point 0x{ord(char):02X})"
            )

        bit_buffer = (bit_buffer << 6) | six_bit_value
        bit_count += 6

        while bit_count >= 8:
            bit_count -= 8
            result.append((bit_buffer >> bit_count) & _BYTE_MASK)
            bit_buffer &= (1 << bit_count) - 1

    return bytes(result)
