from constants import BITS, SIGN_BIT
from utils import validate_bits
from binary_arithmetic import binary_add, binary_subtract_unsigned, binary_compare_unsigned

# В этом модуле операции над binary32 выполняются через знак, порядок и целую мантиссу.
# Встроенный Python float, struct, bin(), format() не используются.

def _parse_decimal_parts(text):
    if text is None:
        raise ValueError("Пустой ввод")
    text = text.strip()
    if not text:
        raise ValueError("Пустой ввод")
    sign = 0
    if text[0] == '-':
        sign = 1
        text = text[1:]
    elif text[0] == '+':
        text = text[1:]
    if not text or text.count('.') > 1:
        raise ValueError("Некорректное вещественное число")
    if '.' in text:
        left, right = text.split('.')
    else:
        left, right = text, ''
    if left == '': left = '0'
    if right == '': right = '0'
    numerator = 0
    for ch in left + right:
        if ch < '0' or ch > '9':
            raise ValueError("Некорректное вещественное число")
        numerator = (numerator << 3) + (numerator << 1) + (ord(ch) - ord('0'))
    denominator = 1
    for _ in right:
        denominator = (denominator << 3) + (denominator << 1)
    return sign, numerator, denominator

def _bit_length(value):
    n = 0
    temp = value
    while temp:
        temp >>= 1
        n += 1
    return n

def _round_shift_right(value, shift):
    if shift <= 0:
        return value << (-shift)
    if shift > 2000:
        return 0
    kept = value >> shift
    dropped_mask = (1 << shift) - 1
    dropped = value & dropped_mask
    half = 1 << (shift - 1)
    if dropped > half or (dropped == half and (kept & 1)):
        kept += 1
    return kept

def _pack(sign, exp, mant):
    bits = [0] * BITS
    bits[SIGN_BIT] = sign
    i = 0
    while i < 23:
        bits[i] = (mant >> i) & 1
        i += 1
    i = 0
    while i < 8:
        bits[23 + i] = (exp >> i) & 1
        i += 1
    return bits

def _unpack(bits):
    validate_bits(bits)
    sign = bits[SIGN_BIT]
    exp = 0
    for i in range(7, -1, -1):
        exp = (exp << 1) + bits[23 + i]
    mant = 0
    for i in range(22, -1, -1):
        mant = (mant << 1) + bits[i]
    return sign, exp, mant

def _normalize_pack(sign, mantissa, exponent):
    if mantissa == 0:
        return [0] * BITS
    while mantissa >= (1 << 24):
        lsb = mantissa & 1
        mantissa >>= 1
        if lsb and (mantissa & 1):
            mantissa += 1
        exponent += 1
    while mantissa < (1 << 23) and exponent > -126:
        mantissa <<= 1
        exponent -= 1
    biased = exponent + 127
    if biased >= 255:
        return _pack(sign, 255, 0)
    if biased <= 0:
        shift = 1 - biased
        mantissa = _round_shift_right(mantissa, shift)
        return _pack(sign, 0, mantissa & ((1 << 23) - 1))
    return _pack(sign, biased, mantissa - (1 << 23))

def decimal_string_to_binary32(text):
    sign, numerator, denominator = _parse_decimal_parts(text)
    if numerator == 0:
        return [0] * BITS
    n_bits = _bit_length(numerator)
    d_bits = _bit_length(denominator)
    exponent = n_bits - d_bits
    # корректировка, чтобы 1 <= numerator / denominator / 2^exponent < 2
    if exponent >= 0:
        if numerator < (denominator << exponent):
            exponent -= 1
    else:
        if (numerator << (-exponent)) < denominator:
            exponent -= 1
    # получаем 24 значащих бита + запас для округления
    precision = 30
    if exponent >= 0:
        scaled_num = numerator << precision
        scaled_den = denominator << exponent
    else:
        scaled_num = numerator << (precision - exponent)
        scaled_den = denominator
    quotient = scaled_num // scaled_den
    mantissa = _round_shift_right(quotient, precision - 23)
    if mantissa >= (1 << 24):
        mantissa >>= 1
        exponent += 1
    return _normalize_pack(sign, mantissa, exponent)

def binary32_to_decimal(bits):
    sign, exp, mant = _unpack(bits)
    if exp == 255:
        return ("-" if sign else "") + ("inf" if mant == 0 else "NaN")
    if exp == 0 and mant == 0:
        return "0.0"
    if exp == 0:
        significand = mant
        exponent = -149
    else:
        significand = (1 << 23) + mant
        exponent = exp - 150
    # точное десятичное приближение до 9 значащих цифр без float
    if exponent >= 0:
        value = significand << exponent
        text = str(value) + ".0"
    else:
        denominator = 1 << (-exponent)
        integer = significand // denominator
        remainder = significand - integer * denominator
        digits = []
        for _ in range(9):
            remainder = (remainder << 3) + (remainder << 1)
            digit = remainder // denominator
            remainder -= digit * denominator
            digits.append(chr(ord('0') + digit))
        frac = ''.join(digits).rstrip('0')
        text = str(integer) + ('.' + frac if frac else '.0')
    if sign and text != "0.0":
        text = '-' + text
    return text

def _components_for_arithmetic(bits):
    sign, exp, mant = _unpack(bits)
    if exp == 0:
        return sign, -126, mant
    return sign, exp - 127, (1 << 23) + mant

def float32_add(a_bits, b_bits):
    sa, ea, ma = _components_for_arithmetic(a_bits)
    sb, eb, mb = _components_for_arithmetic(b_bits)
    if ma == 0: return b_bits[:]
    if mb == 0: return a_bits[:]
    if ea > eb:
        mb = _round_shift_right(mb, ea - eb)
        exp = ea
    elif eb > ea:
        ma = _round_shift_right(ma, eb - ea)
        exp = eb
    else:
        exp = ea
    if sa == sb:
        mant = ma + mb
        sign = sa
    else:
        if ma >= mb:
            mant = ma - mb
            sign = sa
        else:
            mant = mb - ma
            sign = sb
    return _normalize_pack(sign, mant, exp)

def float32_sub(a_bits, b_bits):
    neg_b = b_bits[:]
    neg_b[SIGN_BIT] = 1 - neg_b[SIGN_BIT]
    return float32_add(a_bits, neg_b)

def _multiply_unsigned(x, y):
    result = 0
    shift = 0
    temp = y
    while temp:
        if temp & 1:
            result += x << shift
        temp >>= 1
        shift += 1
    return result

def float32_mul(a_bits, b_bits):
    sa, ea, ma = _components_for_arithmetic(a_bits)
    sb, eb, mb = _components_for_arithmetic(b_bits)
    if ma == 0 or mb == 0:
        return [0] * BITS
    sign = sa ^ sb
    product = _multiply_unsigned(ma, mb)
    exp = ea + eb - 23
    return _normalize_pack(sign, product, exp)

def float32_div(a_bits, b_bits):
    sa, ea, ma = _components_for_arithmetic(a_bits)
    sb, eb, mb = _components_for_arithmetic(b_bits)
    if mb == 0:
        raise ZeroDivisionError("Деление float на ноль")
    if ma == 0:
        return [0] * BITS
    sign = sa ^ sb
    dividend = ma << 27
    quotient = dividend // mb
    exp = ea - eb - 4
    return _normalize_pack(sign, quotient, exp)
