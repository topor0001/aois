"""Главный модуль программы с русскоязычным меню."""

import os
import subprocess
import sys
from bool_parser import BooleanFunctionParser, ParseError
from truth_table import TruthTable
from normal_forms import NormalForms
from post_classes import PostClasses
from zhegalkin import ZhegalkinPolynomial
from minimization_dnf import MinimizationDNF
from minimization_cnf import MinimizationCNF
from karnaugh import KarnaughMap
from differentiation import BooleanDerivative
from constants import SEPARATOR_LENGTH


def setup_console_encoding():
    """Настройка кодировки для корректного русского вывода в Windows."""
    try:
        if os.name == "nt":
            os.system("chcp 65001 > nul")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def print_separator(title: str = ""):
    if title:
        print(f"\n{'=' * SEPARATOR_LENGTH}")
        print(f"  {title}")
        print(f"{'=' * SEPARATOR_LENGTH}")
    else:
        print(f"{'=' * SEPARATOR_LENGTH}")


def print_menu():
    print("\n" + "=" * 60)
    print("  ГЛАВНОЕ МЕНЮ")
    print("=" * 60)
    print("1. Ввести / изменить логическую функцию")
    print("2. Построить таблицу истинности")
    print("3. Вывести СДНФ, СКНФ, числовые и индексную формы")
    print("4. Определить принадлежность к классам Поста")
    print("5. Построить полином Жегалкина")
    print("6. Найти фиктивные переменные")
    print("7. Выполнить булево дифференцирование")
    print("8. Минимизировать ДНФ расчётно-табличным методом")
    print("9. Минимизировать КНФ расчётно-табличным методом")
    print("10. Минимизировать ДНФ и КНФ методом карт Карно")
    print("11. Запустить все тесты и отчёт покрытия")
    print("12. Показать все результаты сразу")
    print("0. Выход")
    print("-" * 60)


def format_logic(text: str) -> str:
    return text.replace('!', '¬').replace('&', '∧').replace('|', '∨').replace('->', '→')


def print_truth_table(table_data, variables):
    header = " | ".join(variables) + " | F"
    print(header)
    print("-" * len(header))
    for values, res in table_data:
        print(" | ".join(str(v) for v in values) + f" | {res}")


def print_sdnf_sknf(forms):
    sdnf_str, sdnf_nums = forms.get_sdnf()
    sknf_str, sknf_nums = forms.get_sknf()
    print(f"СДНФ: {format_logic(sdnf_str)}")
    print(f"Числовая форма СДНФ: {sdnf_nums}")
    print(f"СКНФ: {format_logic(sknf_str)}")
    print(f"Числовая форма СКНФ: {sknf_nums}")
    print(f"Индексная форма функции: {forms.get_index_form()}")


def print_post_classes(post):
    names = {
        'T0 (preserves 0)': 'T0 — сохраняет 0',
        'T1 (preserves 1)': 'T1 — сохраняет 1',
        'S (self-dual)': 'S — самодвойственная',
        'M (monotonic)': 'M — монотонная',
        'L (linear)': 'L — линейная',
    }
    for class_name, belongs in post.get_all().items():
        print(f"  {names.get(class_name, class_name)}: {'да' if belongs else 'нет'}")


def print_minimization_result(result, stages):
    for stage in stages:
        print(f"  {format_logic(stage)}")


def find_fake_variables(truth_table: TruthTable) -> list:
    variables = truth_table.variables
    value_map = {values: res for values, res in truth_table.table}
    fake_vars = []

    for idx, var in enumerate(variables):
        is_fake = True
        for values in value_map:
            neg_values = list(values)
            neg_values[idx] = 1 - neg_values[idx]
            if value_map[values] != value_map[tuple(neg_values)]:
                is_fake = False
                break
        if is_fake:
            fake_vars.append(var)

    return fake_vars


def print_boolean_derivatives(deriv, variables):
    if len(variables) >= 1:
        print(f"  Частная производная по {variables[0]}:")
        for line in deriv.format_result(deriv.partial(variables[0])):
            print(line)
    if len(variables) >= 2:
        print(f"  Смешанная производная по {variables[0]}, {variables[1]}:")
        for line in deriv.format_result(deriv.mixed([variables[0], variables[1]])):
            print(line)


def print_karnaugh_results(karnaugh, variables):
    if len(variables) <= 5:
        result_karnaugh_dnf, map_dnf = karnaugh.minimize_dnf()
        print("  ДНФ:")
        for line in map_dnf:
            print(f"    {format_logic(line)}")
        print(f"    Результат: {format_logic(result_karnaugh_dnf)}")

        result_karnaugh_cnf, map_cnf = karnaugh.minimize_cnf()
        print("  КНФ:")
        for line in map_cnf:
            print(f"    {format_logic(line)}")
        print(f"    Результат: {format_logic(result_karnaugh_cnf)}")
    else:
        print(f"  Карта Карно не поддерживается для {len(variables)} переменных. Максимум: 5")


def run_all_tests():
    print_separator("ЗАПУСК ТЕСТОВ И ОТЧЁТ ПОКРЫТИЯ")
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        test_result = subprocess.run(
            [sys.executable, "-m", "coverage", "run", "-m", "unittest", "discover", "-p", "test_*.py"],
            cwd=project_dir,
            capture_output=False,
            text=True
        )

        print("\n" + "=" * 60)
        print("  ОТЧЁТ ПОКРЫТИЯ")
        print("=" * 60)

        report_result = subprocess.run(
            [sys.executable, "-m", "coverage", "report", "-m"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        print(report_result.stdout)

        if test_result.returncode != 0:
            print("Внимание: часть тестов завершилась с ошибками.")
    except Exception as e:
        print(f"Ошибка запуска тестов: {e}")
        print("Установите coverage командой: pip install coverage")


def run_all_results(parser, truth_table, forms, post, zhegalkin, deriv, variables):
    print_separator("ТАБЛИЦА ИСТИННОСТИ")
    print_truth_table(parser.truth_table(), variables)

    print_separator("НОРМАЛЬНЫЕ ФОРМЫ")
    print_sdnf_sknf(forms)

    print_separator("КЛАССЫ ПОСТА")
    print_post_classes(post)

    print_separator("ПОЛИНОМ ЖЕГАЛКИНА")
    print(f"  {format_logic(zhegalkin.compute())}")

    print_separator("ФИКТИВНЫЕ ПЕРЕМЕННЫЕ")
    fake = find_fake_variables(truth_table)
    print(f"  Фиктивные переменные: {fake}" if fake else "  Фиктивных переменных нет")

    print_separator("БУЛЕВЫ ПРОИЗВОДНЫЕ")
    print_boolean_derivatives(deriv, variables)

    print_separator("МИНИМИЗАЦИЯ ДНФ")
    dnf_min = MinimizationDNF(truth_table)
    result_dnf, stages_dnf = dnf_min.minimize_with_stages()
    print_minimization_result(result_dnf, stages_dnf)

    print_separator("МИНИМИЗАЦИЯ КНФ")
    cnf_min = MinimizationCNF(truth_table)
    result_cnf, stages_cnf = cnf_min.minimize_with_stages()
    print_minimization_result(result_cnf, stages_cnf)

    print_separator("КАРТА КАРНО")
    if len(variables) <= 5:
        print_karnaugh_results(KarnaughMap(truth_table), variables)
    else:
        print(f"  Карта Карно не поддерживается для {len(variables)} переменных. Максимум: 5")


def build_objects(expression: str):
    parser = BooleanFunctionParser(expression)
    variables = parser.variables
    table_data = parser.truth_table()
    truth_table = TruthTable(variables, table_data)
    forms = NormalForms(truth_table)
    post = PostClasses(truth_table)
    zhegalkin = ZhegalkinPolynomial(truth_table)
    deriv = BooleanDerivative(truth_table)
    return parser, truth_table, forms, post, zhegalkin, deriv, variables


def main():
    setup_console_encoding()
    print("Лабораторная работа №2")
    print("Построение СКНФ и СДНФ на основании таблиц истинности")
    print("Допустимые операции: ! или ¬, & или ∧, | или ∨, -> или →, ~")
    print("Допустимые переменные: a, b, c, d, e")

    parser = truth_table = forms = post = zhegalkin = deriv = None
    variables = []

    while True:
        print_menu()
        choice = input("Введите номер пункта меню: ").strip()

        if choice == '0':
            print("Работа программы завершена.")
            break

        elif choice == '1':
            expression = input("Введите логическую функцию: ").strip()
            try:
                parser, truth_table, forms, post, zhegalkin, deriv, variables = build_objects(expression)
                print(f"Функция принята. Найденные переменные: {variables}")
            except ParseError as e:
                print(f"Ошибка разбора выражения: {e}")
                parser = truth_table = forms = post = zhegalkin = deriv = None
                variables = []

        elif choice == '2':
            if parser is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                print_separator("ТАБЛИЦА ИСТИННОСТИ")
                print_truth_table(parser.truth_table(), variables)

        elif choice == '3':
            if forms is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                print_separator("СДНФ, СКНФ И ЧИСЛОВЫЕ ФОРМЫ")
                print_sdnf_sknf(forms)

        elif choice == '4':
            if post is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                print_separator("КЛАССЫ ПОСТА")
                print_post_classes(post)

        elif choice == '5':
            if zhegalkin is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                print_separator("ПОЛИНОМ ЖЕГАЛКИНА")
                print(f"  {format_logic(zhegalkin.compute())}")

        elif choice == '6':
            if truth_table is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                print_separator("ФИКТИВНЫЕ ПЕРЕМЕННЫЕ")
                fake = find_fake_variables(truth_table)
                print(f"  Фиктивные переменные: {fake}" if fake else "  Фиктивных переменных нет")

        elif choice == '7':
            if deriv is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                print_separator("БУЛЕВЫ ПРОИЗВОДНЫЕ")
                print_boolean_derivatives(deriv, variables)

        elif choice == '8':
            if truth_table is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                print_separator("МИНИМИЗАЦИЯ ДНФ")
                result_dnf, stages_dnf = MinimizationDNF(truth_table).minimize_with_stages()
                print_minimization_result(result_dnf, stages_dnf)

        elif choice == '9':
            if truth_table is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                print_separator("МИНИМИЗАЦИЯ КНФ")
                result_cnf, stages_cnf = MinimizationCNF(truth_table).minimize_with_stages()
                print_minimization_result(result_cnf, stages_cnf)

        elif choice == '10':
            if truth_table is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                print_separator("КАРТА КАРНО")
                print_karnaugh_results(KarnaughMap(truth_table), variables)

        elif choice == '11':
            run_all_tests()

        elif choice == '12':
            if parser is None:
                print("Сначала введите функцию: пункт 1.")
            else:
                run_all_results(parser, truth_table, forms, post, zhegalkin, deriv, variables)

        else:
            print("Некорректный пункт меню. Введите число от 0 до 12.")


if __name__ == "__main__":
    main()
