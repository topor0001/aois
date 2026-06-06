"""
Простая проверка покрытия функций тестами без сторонних библиотек.
"""

import ast
from pathlib import Path


EXCLUDED_FUNCTIONS = {
    "main",
    "__init__",
    "print_menu",
    "read_key_from_console",
    "read_value_from_console",
    "add_record_from_console",
    "find_record_from_console",
    "update_record_from_console",
    "delete_record_from_console",
    "process_menu_choice",
    "run_menu",
}
MIN_COVERAGE_PERCENT = 90


def get_function_names(file_path):
    tree = ast.parse(Path(file_path).read_text(encoding="utf-8"))
    names = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name not in EXCLUDED_FUNCTIONS:
            names.append(node.name)

    return sorted(set(names))


def get_called_names(file_path):
    tree = ast.parse(Path(file_path).read_text(encoding="utf-8"))
    names = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            names.append(node.func.id)

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            names.append(node.func.attr)

    return set(names)


def main():
    functions = get_function_names("main.py")
    called_names = get_called_names("tests.py")

    covered = [name for name in functions if name in called_names]
    missed = [name for name in functions if name not in called_names]

    coverage_percent = round(len(covered) / len(functions) * 100, 2)

    print("Функций всего:", len(functions))
    print("Покрыто тестами:", len(covered))
    print("Покрытие функций тестами:", coverage_percent, "%")

    if missed:
        print("Не покрыто:", ", ".join(missed))
    else:
        print("Все функции покрыты")

    if coverage_percent < MIN_COVERAGE_PERCENT:
        raise SystemExit("Покрытие ниже 90%")

    print("Требование покрытия функций больше 90% выполнено")


if __name__ == "__main__":
    main()
