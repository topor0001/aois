from constants import BITS, SIGN_BIT, MAGNITUDE_BITS

def bit_array_to_str(bits, reverse=False):
    source = reversed(bits) if reverse else bits
    return ''.join('1' if b else '0' for b in source)

def validate_bits(bits, size=BITS):
    if len(bits) != size:
        raise ValueError(f"Массив должен содержать {size} бит")
    for bit in bits:
        if bit not in (0, 1):
            raise ValueError("Массив должен содержать только 0 и 1")

def decimal_string_to_nonnegative_int(text):
    if text is None:
        raise ValueError("Пустой ввод")
    text = text.strip()
    if not text:
        raise ValueError("Пустой ввод")
    value = 0
    for ch in text:
        if ch < '0' or ch > '9':
            raise ValueError("Ожидались только десятичные цифры")
        digit = ord(ch) - ord('0')
        value = (value << 3) + (value << 1) + digit
    return value

def int_to_magnitude_bits(value, size=MAGNITUDE_BITS):
    if value < 0:
        raise ValueError("Модуль не может быть отрицательным")
    max_value = (1 << size) - 1
    if value > max_value:
        raise ValueError("Число не помещается в заданное количество бит")
    bits = [0] * size
    i = 0
    while i < size:
        bits[i] = value & 1
        value >>= 1
        i += 1
    return bits

def magnitude_bits_to_int(bits):
    value = 0
    i = len(bits) - 1
    while i >= 0:
        value <<= 1
        if bits[i]:
            value += 1
        i -= 1
    return value

def int_to_bit_array_sm(value):
    sign = 1 if value < 0 else 0
    mag = -value if value < 0 else value
    bits = int_to_magnitude_bits(mag, MAGNITUDE_BITS) + [sign]
    return bits

def bit_array_to_int_sm(bits):
    validate_bits(bits)
    mag = magnitude_bits_to_int(bits[:MAGNITUDE_BITS])
    return -mag if bits[SIGN_BIT] else mag

def int_to_bit_array_twos(value):
    min_value = -(1 << 31)
    max_value = (1 << 31) - 1
    if value < min_value or value > max_value:
        raise ValueError("Число не помещается в 32-битный дополнительный код")
    if value >= 0:
        return int_to_magnitude_bits(value, BITS)
    positive = int_to_magnitude_bits(-value, BITS)
    inverted = [1 - b for b in positive]
    return add_one(inverted)

def bit_array_to_int_twos(bits):
    validate_bits(bits)
    if bits[SIGN_BIT] == 0:
        return magnitude_bits_to_int(bits)
    inverted = [1 - b for b in bits]
    magnitude = add_one(inverted)
    return -magnitude_bits_to_int(magnitude)

def int_to_bit_array_ones(value):
    min_value = -((1 << 31) - 1)
    max_value = (1 << 31) - 1
    if value < min_value or value > max_value:
        raise ValueError("Число не помещается в 32-битный обратный код")
    if value >= 0:
        return int_to_magnitude_bits(value, BITS)
    positive = int_to_magnitude_bits(-value, BITS)
    return [1 - b for b in positive]

def add_one(bits):
    result = bits[:]
    carry = 1
    i = 0
    while i < len(result) and carry:
        s = result[i] + carry
        result[i] = s & 1
        carry = 1 if s > 1 else 0
        i += 1
    return result
