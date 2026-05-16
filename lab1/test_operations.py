import pytest
from utils import *
from binary_arithmetic import *
from bcd2421 import *
from float32 import *

def close_decimal(text, expected, eps=0.01):
    return abs(float(text) - expected) <= eps

def test_direct_ones_twos_codes_roundtrip():
    for value in [0, 1, -1, 5, -5, 123456, -123456, 2**30 - 1, -(2**30 - 1)]:
        assert bit_array_to_int_sm(int_to_bit_array_sm(value)) == value
        assert bit_array_to_int_twos(int_to_bit_array_twos(value)) == value
    assert bit_array_to_str([1,0,1,0]) == '1010'
    assert bit_array_to_str([1,0,1,0], reverse=True) == '0101'

def test_code_range_errors():
    with pytest.raises(ValueError): int_to_bit_array_sm(1 << 31)
    with pytest.raises(ValueError): int_to_bit_array_twos(1 << 31)
    with pytest.raises(ValueError): int_to_bit_array_ones(-(1 << 31))
    with pytest.raises(ValueError): bit_array_to_int_sm([0] * 31)
    with pytest.raises(ValueError): validate_bits([0, 2] + [0] * 30)

def test_twos_add_subtract():
    cases = [(15, 7), (-15, 7), (15, -7), (-10, -20), (0, 0)]
    for a, b in cases:
        res = twos_complement_add(int_to_bit_array_twos(a), int_to_bit_array_twos(b))
        assert bit_array_to_int_twos(res) == a + b
        res = twos_complement_subtract(int_to_bit_array_twos(a), int_to_bit_array_twos(b))
        assert bit_array_to_int_twos(res) == a - b

def test_multiply_direct_code_without_python_operator_interface():
    for a, b in [(5,3), (-5,3), (5,-3), (-5,-3), (0, 7), (123, 456)]:
        res = sign_magnitude_multiply(int_to_bit_array_sm(a), int_to_bit_array_sm(b))
        assert bit_array_to_int_sm(res) == a * b

def test_divide_direct_code():
    dec, binary = sign_magnitude_divide(int_to_bit_array_sm(10), int_to_bit_array_sm(3), 5)
    assert dec == '3.33333'
    assert binary.startswith('11.')
    dec, _ = sign_magnitude_divide(int_to_bit_array_sm(-10), int_to_bit_array_sm(3), 5)
    assert dec == '-3.33333'
    with pytest.raises(ZeroDivisionError):
        sign_magnitude_divide(int_to_bit_array_sm(10), int_to_bit_array_sm(0), 5)

def test_bcd2421_variant_b_32_bits():
    bits = decimal_to_bcd2421_32('123')
    assert len(bits) == 32
    assert bcd2421_32_to_decimal(bits) == '123'
    res = bcd2421_add_32(decimal_to_bcd2421_32('456'), decimal_to_bcd2421_32('789'))
    assert bcd2421_32_to_decimal(res) == '1245'
    res = bcd2421_add_32(decimal_to_bcd2421_32('999'), decimal_to_bcd2421_32('1'))
    assert bcd2421_32_to_decimal(res) == '1000'
    with pytest.raises(ValueError): decimal_to_bcd2421_32('12a3')
    with pytest.raises(ValueError): decimal_to_bcd2421_32('123456789')
    with pytest.raises(OverflowError):
        bcd2421_add_32(decimal_to_bcd2421_32('99999999'), decimal_to_bcd2421_32('1'))

def test_bcd_compatibility_wrappers():
    n = decimal_to_bcd2421('123')
    assert bcd2421_to_decimal(n) == '123'
    assert bcd2421_to_decimal(bcd2421_add(decimal_to_bcd2421('9'), decimal_to_bcd2421('1'))) == '10'

def test_float32_conversion_basic():
    assert binary32_to_decimal(decimal_string_to_binary32('0.0')) == '0.0'
    assert close_decimal(binary32_to_decimal(decimal_string_to_binary32('1.0')), 1.0)
    assert close_decimal(binary32_to_decimal(decimal_string_to_binary32('-1.0')), -1.0)
    assert close_decimal(binary32_to_decimal(decimal_string_to_binary32('3.1415926')), 3.1415926, 0.00001)
    with pytest.raises(ValueError): decimal_string_to_binary32('abc')

def test_float32_operations():
    a = decimal_string_to_binary32('1.5')
    b = decimal_string_to_binary32('2.25')
    assert close_decimal(binary32_to_decimal(float32_add(a, b)), 3.75)
    assert close_decimal(binary32_to_decimal(float32_sub(decimal_string_to_binary32('5.0'), decimal_string_to_binary32('2.0'))), 3.0)
    assert close_decimal(binary32_to_decimal(float32_mul(decimal_string_to_binary32('1.5'), decimal_string_to_binary32('2.0'))), 3.0)
    assert close_decimal(binary32_to_decimal(float32_div(decimal_string_to_binary32('5.0'), decimal_string_to_binary32('2.0'))), 2.5)
    with pytest.raises(ZeroDivisionError): float32_div(a, decimal_string_to_binary32('0.0'))

def test_float_special_values_to_decimal():
    inf = [0] * 32
    for i in range(23, 31): inf[i] = 1
    assert binary32_to_decimal(inf) == 'inf'
    inf[31] = 1
    assert binary32_to_decimal(inf) == '-inf'
    nan = [0] * 32
    for i in range(23, 31): nan[i] = 1
    nan[0] = 1
    assert binary32_to_decimal(nan) == 'NaN'

def test_utils_decimal_parser_and_errors():
    assert decimal_string_to_nonnegative_int('12345') == 12345
    with pytest.raises(ValueError): decimal_string_to_nonnegative_int('')
    with pytest.raises(ValueError): decimal_string_to_nonnegative_int(None)
    with pytest.raises(ValueError): decimal_string_to_nonnegative_int('12a')
    with pytest.raises(ValueError): int_to_magnitude_bits(-1)

def test_binary_algorithm_extra_branches():
    assert binary_compare_unsigned([1, 0, 1], [1, 1, 0]) == 1
    with pytest.raises(ValueError): binary_subtract_unsigned([0], [1])
    q, r = unsigned_divide([0,1,1], [1,1,0], 3)  # 6 / 3
    assert q == [0,1,0]
    assert r == [0,0,0]

def test_float32_extra_branches():
    assert binary32_to_decimal(decimal_string_to_binary32('+0')) == '0.0'
    assert close_decimal(binary32_to_decimal(decimal_string_to_binary32('.5')), 0.5)
    assert close_decimal(binary32_to_decimal(decimal_string_to_binary32('10000000000000000000000000000000000000000')), 1e40, 1e36) or binary32_to_decimal(decimal_string_to_binary32('10000000000000000000000000000000000000000')) == 'inf'
    tiny = decimal_string_to_binary32('0.000000000000000000000000000000000000000000001')
    assert len(tiny) == 32
    assert close_decimal(binary32_to_decimal(float32_add(decimal_string_to_binary32('0.0'), decimal_string_to_binary32('2.0'))), 2.0)
    assert close_decimal(binary32_to_decimal(float32_add(decimal_string_to_binary32('5.0'), decimal_string_to_binary32('-2.0'))), 3.0)
    assert close_decimal(binary32_to_decimal(float32_add(decimal_string_to_binary32('2.0'), decimal_string_to_binary32('-5.0'))), -3.0)
    assert binary32_to_decimal(float32_mul(decimal_string_to_binary32('0.0'), decimal_string_to_binary32('5.0'))) == '0.0'
    assert binary32_to_decimal(float32_div(decimal_string_to_binary32('0.0'), decimal_string_to_binary32('5.0'))) == '0.0'
    with pytest.raises(ValueError): decimal_string_to_binary32('1.2.3')
    with pytest.raises(ValueError): decimal_string_to_binary32('')

def test_main_handlers_and_menu(monkeypatch, capsys):
    import main
    main.show_menu()
    assert 'ЛАБОРАТОРНАЯ' in capsys.readouterr().out
    data = iter(['5'])
    monkeypatch.setattr('builtins.input', lambda _: next(data))
    main.handle_convert()
    assert 'Прямой код' in capsys.readouterr().out
    data = iter(['15', '7'])
    monkeypatch.setattr('builtins.input', lambda _: next(data))
    main.handle_add()
    assert '22' in capsys.readouterr().out
    data = iter(['15', '7'])
    monkeypatch.setattr('builtins.input', lambda _: next(data))
    main.handle_subtract()
    assert '8' in capsys.readouterr().out
    data = iter(['5', '3'])
    monkeypatch.setattr('builtins.input', lambda _: next(data))
    main.handle_multiply()
    assert '15' in capsys.readouterr().out
    data = iter(['10', '3'])
    monkeypatch.setattr('builtins.input', lambda _: next(data))
    main.handle_divide()
    assert '3.33333' in capsys.readouterr().out
    data = iter(['1', '1.5', '2.25'])
    monkeypatch.setattr('builtins.input', lambda _: next(data))
    main.handle_float32()
    assert '3.75' in capsys.readouterr().out
    data = iter(['456', '789'])
    monkeypatch.setattr('builtins.input', lambda _: next(data))
    main.handle_bcd()
    assert '1245' in capsys.readouterr().out

def test_main_loop_and_input_validation(monkeypatch, capsys):
    import main
    data = iter(['x', '0'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(data))
    main.main()
    out = capsys.readouterr().out
    assert 'такого пункта меню нет' in out
    assert 'Завершение' in out
    data = iter(['', 'abc', '10'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(data))
    assert main.get_int('n=') == 10
    data = iter(['', 'ok'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(data))
    assert main.get_text('t=') == 'ok'

def test_main_tests_menu_item_success(monkeypatch, capsys):
    import main
    calls = []
    def fake_run_command(command):
        calls.append(command)
        return 0
    monkeypatch.setattr(main, 'run_command', fake_run_command)
    main.handle_tests_and_coverage()
    out = capsys.readouterr().out
    assert 'Unit-тестов' in out
    assert 'Отчёт покрытия' in out
    assert len(calls) == 3


def test_main_tests_menu_item_failure(monkeypatch, capsys):
    import main
    monkeypatch.setattr(main, 'run_command', lambda command: 1)
    main.handle_tests_and_coverage()
    assert 'Покрытие не запускается' in capsys.readouterr().out


def test_main_float_invalid_operation(monkeypatch, capsys):
    import main
    data = iter(['9', '1.0', '2.0'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(data))
    main.handle_float32()
    assert 'неизвестная операция' in capsys.readouterr().out


def test_main_loop_runs_tests_item(monkeypatch, capsys):
    import main
    monkeypatch.setattr(main, 'handle_tests_and_coverage', lambda: print('ТЕСТЫ ЗАПУЩЕНЫ'))
    data = iter(['8', '0'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(data))
    main.main()
    out = capsys.readouterr().out
    assert 'ТЕСТЫ ЗАПУЩЕНЫ' in out
