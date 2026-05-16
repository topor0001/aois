from constants import BITS, BCD_DIGITS_IN_32_BITS

BCD_2421 = [
    [0,0,0,0], [0,0,0,1], [0,0,1,0], [0,0,1,1], [0,1,0,0],
    [1,0,1,1], [1,1,0,0], [1,1,0,1], [1,1,1,0], [1,1,1,1]
]

def digit_from_nibble(nibble):
    for i in range(10):
        if BCD_2421[i] == nibble:
            return i
    raise ValueError("Недопустимая тетрада BCD-2421")

def decimal_to_bcd2421_32(text):
    if text is None:
        raise ValueError("Пустой ввод")
    text = text.strip()
    if not text:
        raise ValueError("Пустой ввод")
    if len(text) > BCD_DIGITS_IN_32_BITS:
        raise ValueError("BCD-2421 в 32 битах хранит максимум 8 десятичных цифр")
    for ch in text:
        if ch < '0' or ch > '9':
            raise ValueError("BCD-2421 принимает только цифры 0..9")
    padded = '0' * (BCD_DIGITS_IN_32_BITS - len(text)) + text
    bits = []
    for ch in padded:
        bits.extend(BCD_2421[ord(ch) - ord('0')])
    return bits

def bcd2421_32_to_decimal(bits):
    if len(bits) != BITS:
        raise ValueError("BCD-массив должен содержать 32 бита")
    digits = []
    for i in range(0, BITS, 4):
        digits.append(chr(ord('0') + digit_from_nibble(bits[i:i+4])))
    text = ''.join(digits).lstrip('0')
    return text if text else '0'

def bcd2421_add_32(a_bits, b_bits):
    if len(a_bits) != BITS or len(b_bits) != BITS:
        raise ValueError("BCD-массив должен содержать 32 бита")
    result_digits = [0] * BCD_DIGITS_IN_32_BITS
    carry = 0
    pos = BCD_DIGITS_IN_32_BITS - 1
    while pos >= 0:
        start = pos * 4
        a_digit = digit_from_nibble(a_bits[start:start+4])
        b_digit = digit_from_nibble(b_bits[start:start+4])
        total = a_digit + b_digit + carry
        if total >= 10:
            total -= 10
            carry = 1
        else:
            carry = 0
        result_digits[pos] = total
        pos -= 1
    if carry:
        raise OverflowError("Результат BCD-2421 не помещается в 32 бита")
    result = []
    for d in result_digits:
        result.extend(BCD_2421[d])
    return result

# Совместимые обёртки для тестов старого формата.
def decimal_to_bcd2421(text):
    bits = decimal_to_bcd2421_32(text)
    start = BITS - len(text.strip()) * 4
    return [bits[i:i+4] for i in range(start, BITS, 4)]

def bcd2421_to_decimal(nibbles):
    return ''.join(chr(ord('0') + digit_from_nibble(n)) for n in nibbles).lstrip('0') or '0'

def bcd2421_add(a_nibbles, b_nibbles):
    a = []
    b = []
    for n in a_nibbles: a.extend(n)
    for n in b_nibbles: b.extend(n)
    a = [0] * (BITS - len(a)) + a
    b = [0] * (BITS - len(b)) + b
    res = bcd2421_add_32(a, b)
    text = bcd2421_32_to_decimal(res)
    return decimal_to_bcd2421(text)
