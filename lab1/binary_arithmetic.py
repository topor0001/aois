from constants import BITS, SIGN_BIT, MAGNITUDE_BITS
from utils import validate_bits, bit_array_to_int_sm, bit_array_to_int_twos

def binary_add(a, b, carry_in=0, size=None):
    if size is None:
        size = max(len(a), len(b))
    result = [0] * size
    carry = carry_in
    i = 0
    while i < size:
        av = a[i] if i < len(a) else 0
        bv = b[i] if i < len(b) else 0
        s = av + bv + carry
        result[i] = s & 1
        carry = 1 if s > 1 else 0
        i += 1
    return result, carry

def binary_compare_unsigned(a, b):
    size = max(len(a), len(b))
    i = size - 1
    while i >= 0:
        av = a[i] if i < len(a) else 0
        bv = b[i] if i < len(b) else 0
        if av > bv:
            return 1
        if av < bv:
            return -1
        i -= 1
    return 0

def binary_subtract_unsigned(a, b):
    if binary_compare_unsigned(a, b) < 0:
        raise ValueError("Отрицательный результат в беззнаковом вычитании")
    size = max(len(a), len(b))
    result = [0] * size
    borrow = 0
    i = 0
    while i < size:
        av = a[i] if i < len(a) else 0
        bv = b[i] if i < len(b) else 0
        val = av - bv - borrow
        if val < 0:
            val += 2
            borrow = 1
        else:
            borrow = 0
        result[i] = val
        i += 1
    return result

def shift_left(bits, places, size):
    result = [0] * size
    i = 0
    while i < len(bits):
        target = i + places
        if target < size:
            result[target] = bits[i]
        i += 1
    return result

def twos_complement_add(a_bits, b_bits):
    validate_bits(a_bits)
    validate_bits(b_bits)
    result, _ = binary_add(a_bits, b_bits, 0, BITS)
    return result

def twos_complement_negate(bits):
    validate_bits(bits)
    inverted = [1 - b for b in bits]
    one = [1] + [0] * (BITS - 1)
    result, _ = binary_add(inverted, one, 0, BITS)
    return result

def twos_complement_subtract(a_bits, b_bits):
    return twos_complement_add(a_bits, twos_complement_negate(b_bits))

def sign_magnitude_multiply(a_bits, b_bits):
    validate_bits(a_bits)
    validate_bits(b_bits)
    result_sign = a_bits[SIGN_BIT] ^ b_bits[SIGN_BIT]
    mag_a = a_bits[:MAGNITUDE_BITS]
    mag_b = b_bits[:MAGNITUDE_BITS]
    product = [0] * MAGNITUDE_BITS
    i = 0
    while i < MAGNITUDE_BITS:
        if mag_b[i] == 1:
            shifted = shift_left(mag_a, i, MAGNITUDE_BITS)
            product, _ = binary_add(product, shifted, 0, MAGNITUDE_BITS)
        i += 1
    return product + [result_sign]

def unsigned_divide(dividend, divisor, quotient_size):
    if binary_compare_unsigned(divisor, [0] * len(divisor)) == 0:
        raise ZeroDivisionError("Деление на ноль")
    remainder = [0] * len(dividend)
    quotient = [0] * quotient_size
    i = len(dividend) - 1
    qpos = quotient_size - 1
    while i >= 0 and qpos >= 0:
        remainder = shift_left(remainder, 1, len(remainder))
        remainder[0] = dividend[i]
        if binary_compare_unsigned(remainder, divisor) >= 0:
            remainder = binary_subtract_unsigned(remainder, divisor)
            quotient[qpos] = 1
        i -= 1
        qpos -= 1
    return quotient, remainder

def sign_magnitude_divide(dividend_bits, divisor_bits, decimal_places=5):
    validate_bits(dividend_bits)
    validate_bits(divisor_bits)
    result_sign = dividend_bits[SIGN_BIT] ^ divisor_bits[SIGN_BIT]
    mag_dividend = dividend_bits[:MAGNITUDE_BITS]
    mag_divisor = divisor_bits[:MAGNITUDE_BITS]
    if binary_compare_unsigned(mag_divisor, [0] * MAGNITUDE_BITS) == 0:
        raise ZeroDivisionError("Деление на ноль")
    integer_bits, remainder = unsigned_divide(mag_dividend, mag_divisor, MAGNITUDE_BITS)
    int_value = 0
    for i in range(MAGNITUDE_BITS - 1, -1, -1):
        int_value = (int_value << 1) + integer_bits[i]
    frac_digits = []
    r = remainder[:]
    for _ in range(decimal_places):
        # r *= 10 через сдвиги: r*8 + r*2
        r8 = shift_left(r, 3, MAGNITUDE_BITS)
        r2 = shift_left(r, 1, MAGNITUDE_BITS)
        r, _ = binary_add(r8, r2, 0, MAGNITUDE_BITS)
        digit = 0
        while binary_compare_unsigned(r, mag_divisor) >= 0:
            r = binary_subtract_unsigned(r, mag_divisor)
            digit += 1
        frac_digits.append(chr(ord('0') + digit))
    dec = str(int_value) + "." + ''.join(frac_digits)
    if result_sign and (int_value != 0 or any(ch != '0' for ch in frac_digits)):
        dec = '-' + dec
    # binary fixed representation
    binary_int = "0"
    started = False
    chars = []
    for i in range(MAGNITUDE_BITS - 1, -1, -1):
        if integer_bits[i] or started:
            started = True
            chars.append('1' if integer_bits[i] else '0')
    if chars:
        binary_int = ''.join(chars)
    frac_bits = []
    r = remainder[:]
    for _ in range(32):
        r = shift_left(r, 1, MAGNITUDE_BITS)
        if binary_compare_unsigned(r, mag_divisor) >= 0:
            r = binary_subtract_unsigned(r, mag_divisor)
            frac_bits.append('1')
        else:
            frac_bits.append('0')
    binary = binary_int + '.' + ''.join(frac_bits)
    if result_sign:
        binary = '-' + binary
    return dec, binary
