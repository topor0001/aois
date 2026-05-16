import subprocess
import sys

from utils import *
from binary_arithmetic import *
from bcd2421 import *
from float32 import *


def print_bits(bits):
    print(bit_array_to_str(bits, reverse=True))


def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число.")


def get_text(prompt):
    value = input(prompt).strip()
    while not value:
        print("Ошибка: ввод не должен быть пустым.")
        value = input(prompt).strip()
    return value


def show_menu():
    print("\n" + "=" * 64)
    print("ЛАБОРАТОРНАЯ РАБОТА №1. Представление чисел в памяти компьютера")
    print("Вариант b: BCD-2421")
    print("1. Перевод целого числа в прямой, обратный и дополнительный коды")
    print("2. Сложение двух целых чисел в дополнительном коде")
    print("3. Вычитание через отрицание вычитаемого и сложение")
    print("4. Умножение двух целых чисел в прямом коде")
    print("5. Деление двух целых чисел в прямом коде с точностью 5 знаков")
    print("6. Операции IEEE-754 binary32")
    print("7. Сложение двух чисел в BCD-2421")
    print("8. Запустить Unit-тесты и показать покрытие кода")
    print("0. Выход")


def handle_convert():
    value = get_int("Введите целое число: ")
    print("Прямой код:        ", end=""); print_bits(int_to_bit_array_sm(value))
    print("Обратный код:      ", end=""); print_bits(int_to_bit_array_ones(value))
    print("Дополнительный код:", end=""); print_bits(int_to_bit_array_twos(value))
    print("Десятичная проверка:", value)


def handle_add():
    a = get_int("Первое число: ")
    b = get_int("Второе число: ")
    res_bits = twos_complement_add(int_to_bit_array_twos(a), int_to_bit_array_twos(b))
    print(f"Результат: {a} + {b} = {bit_array_to_int_twos(res_bits)}")
    print("Двоичный результат:", end=" "); print_bits(res_bits)


def handle_subtract():
    a = get_int("Уменьшаемое: ")
    b = get_int("Вычитаемое: ")
    res_bits = twos_complement_subtract(int_to_bit_array_twos(a), int_to_bit_array_twos(b))
    print(f"Результат: {a} - {b} = {bit_array_to_int_twos(res_bits)}")
    print("Двоичный результат:", end=" "); print_bits(res_bits)


def handle_multiply():
    a = get_int("Первый множитель: ")
    b = get_int("Второй множитель: ")
    res_bits = sign_magnitude_multiply(int_to_bit_array_sm(a), int_to_bit_array_sm(b))
    print(f"Результат: {a} * {b} = {bit_array_to_int_sm(res_bits)}")
    print("Двоичный результат:", end=" "); print_bits(res_bits)


def handle_divide():
    a = get_int("Делимое: ")
    b = get_int("Делитель: ")
    dec, binary = sign_magnitude_divide(int_to_bit_array_sm(a), int_to_bit_array_sm(b), 5)
    print(f"Результат: {a} / {b} = {dec}")
    print("Двоичный результат:", binary)


def handle_float32():
    print("Операция: 1 - сложение, 2 - вычитание, 3 - умножение, 4 - деление")
    op = get_text("Выбор: ")
    a = get_text("Первое вещественное число: ")
    b = get_text("Второе вещественное число: ")
    a_bits = decimal_string_to_binary32(a)
    b_bits = decimal_string_to_binary32(b)
    if op == '1':
        res = float32_add(a_bits, b_bits)
        sign = '+'
    elif op == '2':
        res = float32_sub(a_bits, b_bits)
        sign = '-'
    elif op == '3':
        res = float32_mul(a_bits, b_bits)
        sign = '*'
    elif op == '4':
        res = float32_div(a_bits, b_bits)
        sign = '/'
    else:
        print("Ошибка: неизвестная операция.")
        return
    print(f"Результат: {a} {sign} {b} = {binary32_to_decimal(res)}")
    print("Двоичное представление binary32:", end=" "); print_bits(res)


def handle_bcd():
    a = get_text("Первое десятичное число, максимум 8 цифр: ")
    b = get_text("Второе десятичное число, максимум 8 цифр: ")
    a_bits = decimal_to_bcd2421_32(a)
    b_bits = decimal_to_bcd2421_32(b)
    res = bcd2421_add_32(a_bits, b_bits)
    print(f"Результат: {a} + {b} = {bcd2421_32_to_decimal(res)}")
    print("BCD-2421, 32 бита:", bit_array_to_str(res))


def run_command(command):
    completed = subprocess.run(command, text=True)
    return completed.returncode


def handle_tests_and_coverage():
    print("\nЗапуск Unit-тестов с подробным выводом названий тестов...")
    print("-" * 64)
    tests_code = run_command([sys.executable, "-m", "pytest", "-v", "test_operations.py"])
    if tests_code != 0:
        print("\nТесты завершились с ошибками. Покрытие не запускается.")
        return

    print("\nВсе тесты прошли успешно.")
    print("\nЗапуск проверки покрытия кода...")
    print("-" * 64)
    coverage_code = run_command([
        sys.executable, "-m", "coverage", "run",
        "--source=.",
        "--omit=test_operations.py",
        "-m", "pytest", "test_operations.py"
    ])
    if coverage_code != 0:
        print("Ошибка при запуске coverage.")
        return
    print("\nОтчёт покрытия по файлам:")
    print("-" * 64)
    run_command([sys.executable, "-m", "coverage", "report", "-m"])


def main():
    actions = {
        '1': handle_convert,
        '2': handle_add,
        '3': handle_subtract,
        '4': handle_multiply,
        '5': handle_divide,
        '6': handle_float32,
        '7': handle_bcd,
        '8': handle_tests_and_coverage,
    }
    while True:
        show_menu()
        choice = input("Выберите пункт: ").strip()
        if choice == '0':
            print("Завершение программы.")
            break
        action = actions.get(choice)
        if action is None:
            print("Ошибка: такого пункта меню нет.")
            continue
        try:
            action()
        except Exception as exc:
            print("Ошибка:", exc)


if __name__ == "__main__":
    main()
