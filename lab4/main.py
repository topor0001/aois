"""
Лабораторная работа №4.
Хеш-таблица. Вариант 6:
разрешение коллизий с помощью цепочек на базе сбалансированного дерева.

Без сторонних библиотек.
"""

from __future__ import annotations

import os
import subprocess
import sys

from typing import Optional


TABLE_SIZE = 20
BASE_ADDRESS = 0
RUSSIAN_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
POSITIONAL_BASE = len(RUSSIAN_ALPHABET)
MIN_TABLE_SIZE = 20
MIN_INITIAL_RECORDS = 10
MIN_COLLISIONS = 2
MIN_CHAIN_RECORDS = 3
EMPTY_TEXT = "-"
ROOT_LINK_FLAG = 1
DATA_LINK_FLAG = 0


class DuplicateKeyError(Exception):
    """Ошибка добавления записи с уже существующим ключом."""


class KeyNotFoundError(Exception):
    """Ошибка обращения к несуществующему ключу."""


class AvlNode:
    """Узел сбалансированного дерева AVL."""

    def __init__(self, key: str, value: str, numeric_value: int, hash_address: int):
        self.key = key
        self.value = value
        self.numeric_value = numeric_value
        self.hash_address = hash_address
        self.height = 1
        self.left: Optional[AvlNode] = None
        self.right: Optional[AvlNode] = None


def normalize_key(key: str) -> str:
    """Нормализует ключ для вычислений и сравнений."""
    normalized_key = key.strip().upper()

    if not normalized_key:
        raise ValueError("Ключ не может быть пустым")

    return normalized_key


def get_letter_index(letter: str) -> int:
    """Возвращает номер русской буквы в алфавите."""
    normalized_letter = normalize_key(letter)[0]

    if normalized_letter not in RUSSIAN_ALPHABET:
        raise ValueError("Ключ должен начинаться с русской буквы")

    return RUSSIAN_ALPHABET.index(normalized_letter)


def calculate_numeric_value(key: str) -> int:
    """Вычисляет V по первым двум буквам ключевого слова."""
    normalized_key = normalize_key(key)
    first_letter = normalized_key[0]
    second_letter = normalized_key[1] if len(normalized_key) > 1 else normalized_key[0]

    return (
        get_letter_index(first_letter) * POSITIONAL_BASE
        + get_letter_index(second_letter)
    )


def calculate_hash_address(key: str) -> int:
    """Вычисляет h(V) = V mod H + B."""
    return calculate_numeric_value(key) % TABLE_SIZE + BASE_ADDRESS


def get_height(node: Optional[AvlNode]) -> int:
    """Возвращает высоту узла AVL-дерева."""
    if node is None:
        return 0

    return node.height


def update_height(node: AvlNode) -> None:
    """Обновляет высоту узла AVL-дерева."""
    node.height = max(get_height(node.left), get_height(node.right)) + 1


def get_balance_factor(node: Optional[AvlNode]) -> int:
    """Вычисляет баланс-фактор узла."""
    if node is None:
        return 0

    return get_height(node.left) - get_height(node.right)


def rotate_right(root: AvlNode) -> AvlNode:
    """Выполняет правый поворот AVL-дерева."""
    new_root = root.left
    moved_subtree = new_root.right

    new_root.right = root
    root.left = moved_subtree

    update_height(root)
    update_height(new_root)

    return new_root


def rotate_left(root: AvlNode) -> AvlNode:
    """Выполняет левый поворот AVL-дерева."""
    new_root = root.right
    moved_subtree = new_root.left

    new_root.left = root
    root.right = moved_subtree

    update_height(root)
    update_height(new_root)

    return new_root


def balance_node(node: AvlNode) -> AvlNode:
    """Балансирует узел AVL-дерева."""
    update_height(node)
    balance_factor = get_balance_factor(node)

    if balance_factor > 1:
        if get_balance_factor(node.left) < 0:
            node.left = rotate_left(node.left)

        return rotate_right(node)

    if balance_factor < -1:
        if get_balance_factor(node.right) > 0:
            node.right = rotate_right(node.right)

        return rotate_left(node)

    return node


def insert_avl_node(
    root: Optional[AvlNode],
    key: str,
    value: str,
    numeric_value: int,
    hash_address: int,
) -> AvlNode:
    """Добавляет запись в AVL-дерево."""
    if root is None:
        return AvlNode(key, value, numeric_value, hash_address)

    if key == root.key:
        raise DuplicateKeyError("Ключ уже существует")

    if key < root.key:
        root.left = insert_avl_node(root.left, key, value, numeric_value, hash_address)
    else:
        root.right = insert_avl_node(root.right, key, value, numeric_value, hash_address)

    return balance_node(root)


def find_avl_node(root: Optional[AvlNode], key: str) -> Optional[AvlNode]:
    """Ищет узел в AVL-дереве."""
    current_node = root

    while current_node is not None:
        if key == current_node.key:
            return current_node

        if key < current_node.key:
            current_node = current_node.left
        else:
            current_node = current_node.right

    return None


def find_min_node(root: AvlNode) -> AvlNode:
    """Ищет минимальный узел в AVL-дереве."""
    current_node = root

    while current_node.left is not None:
        current_node = current_node.left

    return current_node


def delete_avl_node(root: Optional[AvlNode], key: str) -> Optional[AvlNode]:
    """Удаляет узел из AVL-дерева."""
    if root is None:
        raise KeyNotFoundError("Ключ не найден")

    if key < root.key:
        root.left = delete_avl_node(root.left, key)
    elif key > root.key:
        root.right = delete_avl_node(root.right, key)
    else:
        if root.left is None:
            return root.right

        if root.right is None:
            return root.left

        successor = find_min_node(root.right)
        root.key = successor.key
        root.value = successor.value
        root.numeric_value = successor.numeric_value
        root.hash_address = successor.hash_address
        root.right = delete_avl_node(root.right, successor.key)

    return balance_node(root)


def traverse_avl(root: Optional[AvlNode]) -> list[AvlNode]:
    """Возвращает записи дерева в порядке возрастания ключей."""
    if root is None:
        return []

    return traverse_avl(root.left) + [root] + traverse_avl(root.right)


def count_avl_nodes(root: Optional[AvlNode]) -> int:
    """Возвращает количество узлов AVL-дерева."""
    return len(traverse_avl(root))


def format_avl_node(node: Optional[AvlNode], level: int = 0, branch_name: str = "ROOT") -> list[str]:
    """Формирует текстовое представление AVL-дерева с высотой и балансом."""
    if node is None:
        return []

    indent = "  " * level
    node_line = (
        f"{indent}{branch_name}: {node.key} "
        f"(height={node.height}, balance={get_balance_factor(node)}, "
        f"V={node.numeric_value}, h={node.hash_address})"
    )

    lines = [node_line]
    lines.extend(format_avl_node(node.left, level + 1, "L"))
    lines.extend(format_avl_node(node.right, level + 1, "R"))

    return lines


def print_avl_tree(root: Optional[AvlNode]) -> None:
    """Печатает структуру одного AVL-дерева."""
    if root is None:
        print(EMPTY_TEXT)
        return

    for line in format_avl_node(root):
        print(line)


class HashTable:
    """Хеш-таблица с цепочками в виде сбалансированных деревьев."""

    def __init__(self, size: int = TABLE_SIZE):
        if size < MIN_TABLE_SIZE:
            raise ValueError("Размер таблицы должен быть не менее 20 строк")

        self.size = size
        self.buckets: list[Optional[AvlNode]] = [None] * size
        self.records_count = 0

    def create(self, key: str, value: str) -> None:
        """Добавляет новую запись."""
        normalized_key = normalize_key(key)
        numeric_value = calculate_numeric_value(normalized_key)
        hash_address = calculate_hash_address(normalized_key)

        if self.read(normalized_key, raise_error=False) is not None:
            raise DuplicateKeyError("Ключ уже существует")

        self.buckets[hash_address] = insert_avl_node(
            self.buckets[hash_address],
            normalized_key,
            value,
            numeric_value,
            hash_address,
        )
        self.records_count += 1

    def read(self, key: str, raise_error: bool = True) -> Optional[str]:
        """Ищет данные по ключу."""
        normalized_key = normalize_key(key)
        hash_address = calculate_hash_address(normalized_key)
        found_node = find_avl_node(self.buckets[hash_address], normalized_key)

        if found_node is None:
            if raise_error:
                raise KeyNotFoundError("Ключ не найден")

            return None

        return found_node.value

    def update(self, key: str, value: str) -> None:
        """Обновляет данные по ключу."""
        normalized_key = normalize_key(key)
        hash_address = calculate_hash_address(normalized_key)
        found_node = find_avl_node(self.buckets[hash_address], normalized_key)

        if found_node is None:
            raise KeyNotFoundError("Ключ не найден")

        found_node.value = value

    def delete(self, key: str) -> None:
        """Удаляет запись по ключу."""
        normalized_key = normalize_key(key)
        hash_address = calculate_hash_address(normalized_key)

        self.buckets[hash_address] = delete_avl_node(
            self.buckets[hash_address],
            normalized_key,
        )
        self.records_count -= 1

    def get_load_factor(self) -> float:
        """Возвращает коэффициент заполнения."""
        return self.records_count / self.size

    def get_collision_count(self) -> int:
        """Возвращает количество бакетов, в которых есть коллизии."""
        collision_count = 0

        for bucket in self.buckets:
            if count_avl_nodes(bucket) > 1:
                collision_count += 1

        return collision_count

    def get_chain_records_count(self) -> int:
        """Возвращает количество записей в коллизионных деревьях."""
        chain_records_count = 0

        for bucket in self.buckets:
            nodes_count = count_avl_nodes(bucket)

            if nodes_count > 1:
                chain_records_count += nodes_count

        return chain_records_count

    def get_all_records(self) -> list[AvlNode]:
        """Возвращает все записи таблицы."""
        records = []

        for bucket in self.buckets:
            records.extend(traverse_avl(bucket))

        return records

    def print_hash_values(self) -> None:
        """Печатает V и h(V) для каждой записи."""
        print("\nВычисленные значения V и h(V)")

        for node in self.get_all_records():
            print(node.key, "V =", node.numeric_value, "h =", node.hash_address)

    def print_table(self) -> None:
        """Печатает все строки хеш-таблицы."""
        print("\nХеш-таблица")
        print("№ | ID | C | U | T | L | D | P0 | Pi")

        for index, bucket in enumerate(self.buckets):
            nodes = traverse_avl(bucket)
            is_occupied = int(bool(nodes))
            is_collision = int(len(nodes) > 1)
            is_terminal = int(len(nodes) <= 1)
            link_flag = ROOT_LINK_FLAG if nodes else DATA_LINK_FLAG
            delete_flag = 0
            root_pointer = bucket.key if bucket else EMPTY_TEXT
            data_text = (
                "; ".join(f"{node.key}: {node.value}" for node in nodes)
                if nodes
                else EMPTY_TEXT
            )

            print(
                index,
                "|",
                root_pointer,
                "|",
                is_collision,
                "|",
                is_occupied,
                "|",
                is_terminal,
                "|",
                link_flag,
                "|",
                delete_flag,
                "|",
                root_pointer,
                "|",
                data_text,
            )

    def print_avl_structures(self) -> None:
        """Печатает структуру AVL-деревьев во всех занятых бакетах."""
        print("\nСтруктура AVL-деревьев в бакетах")

        for index, bucket in enumerate(self.buckets):
            if bucket is not None:
                nodes_count = count_avl_nodes(bucket)
                print(f"\nБакет {index}: записей = {nodes_count}")
                print_avl_tree(bucket)


def build_default_literature_records() -> list[tuple[str, str]]:
    """Возвращает исходные данные по тематике 'Литература'."""
    return [
        ("Роман", "крупное эпическое произведение"),
        ("Романтизм", "литературное направление"),
        ("Романс", "лирическое музыкально-поэтическое произведение"),
        ("Поэма", "крупное стихотворное произведение"),
        ("Поэт", "автор стихотворных произведений"),
        ("Поэзия", "искусство художественного слова в стихах"),
        ("Лирика", "род литературы о чувствах автора"),
        ("Литература", "искусство письменного слова"),
        ("Литота", "художественное преуменьшение"),
        ("Драма", "род литературы для сценического действия"),
        ("Эпитет", "образное художественное определение"),
        ("Басня", "короткое нравоучительное произведение"),
    ]


def build_default_hash_table() -> HashTable:
    """Формирует демонстрационную хеш-таблицу."""
    hash_table = HashTable(TABLE_SIZE)

    for key, value in build_default_literature_records():
        hash_table.create(key, value)

    return hash_table


def validate_lab_requirements(hash_table: HashTable) -> bool:
    """Проверяет основные требования лабораторной работы."""
    has_valid_size = hash_table.size >= MIN_TABLE_SIZE
    has_enough_records = hash_table.records_count >= MIN_INITIAL_RECORDS
    has_enough_collisions = hash_table.get_collision_count() >= MIN_COLLISIONS
    has_enough_chain_records = hash_table.get_chain_records_count() >= MIN_CHAIN_RECORDS

    return (
        has_valid_size
        and has_enough_records
        and has_enough_collisions
        and has_enough_chain_records
    )


def demonstrate_crud(hash_table: HashTable) -> None:
    """Демонстрирует CRUD операции."""
    print("\nCRUD демонстрация")

    hash_table.create("Сатира", "обличение недостатков через насмешку")
    print("CREATE: добавлена запись САТИРА")

    found_value = hash_table.read("Сатира")
    print("READ: САТИРА ->", found_value)

    hash_table.update("Сатира", "жанр обличительной литературы")
    updated_value = hash_table.read("Сатира")
    print("UPDATE: САТИРА ->", updated_value)

    hash_table.delete("Сатира")
    print("DELETE: запись САТИРА удалена")


def print_statistics(hash_table: HashTable) -> None:
    """Печатает коэффициент заполнения и сведения о коллизиях."""
    print("\nСтатистика хеш-таблицы")
    print("Коэффициент заполнения:", hash_table.get_load_factor())
    print("Количество коллизионных бакетов:", hash_table.get_collision_count())
    print("Записей в коллизионных деревьях:", hash_table.get_chain_records_count())

    if validate_lab_requirements(hash_table):
        print("Требования лабораторной работы выполнены")
    else:
        print("Требования лабораторной работы не выполнены")


def run_python_script(script_name: str) -> None:
    """Запускает отдельный Python-файл из папки проекта и печатает результат."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(project_dir, script_name)

    if not os.path.exists(script_path):
        print("Ошибка: файл не найден:", script_path)
        return

    print("\nЗапуск файла:", script_name)

    completed_process = subprocess.run(
        [sys.executable, script_path],
        cwd=project_dir,
        text=True,
        capture_output=True
    )

    if completed_process.stdout:
        print(completed_process.stdout)

    if completed_process.stderr:
        print("Ошибки выполнения:")
        print(completed_process.stderr)

    if completed_process.returncode == 0:
        print("Команда выполнена успешно")
    else:
        print("Команда завершилась с кодом:", completed_process.returncode)


def run_unit_tests_from_menu() -> None:
    """Запускает unit-тесты из меню."""
    run_python_script("tests.py")


def run_coverage_check_from_menu() -> None:
    """Запускает проверку покрытия функций из меню."""
    run_python_script("coverage_check.py")


def print_menu() -> None:
    """Печатает меню программы."""
    print("\n========== МЕНЮ ==========")
    print("1. Показать V и h(V) для всех записей")
    print("2. Показать хеш-таблицу")
    print("3. Добавить запись")
    print("4. Найти запись")
    print("5. Изменить запись")
    print("6. Удалить запись")
    print("7. Показать статистику")
    print("8. Демонстрация CRUD")
    print("9. Показать все результаты лабораторной")
    print("10. Запустить unit-тесты")
    print("11. Показать покрытие функций тестами")
    print("12. Показать структуру AVL-деревьев")
    print("0. Выход")


def read_key_from_console() -> str:
    """Считывает ключ из консоли."""
    return input("Введите ключевое слово: ").strip()


def read_value_from_console() -> str:
    """Считывает данные из консоли."""
    return input("Введите данные: ").strip()


def add_record_from_console(hash_table: HashTable) -> None:
    """Добавляет запись через консольный ввод."""
    key = read_key_from_console()
    value = read_value_from_console()
    hash_table.create(key, value)
    print("Запись добавлена")


def find_record_from_console(hash_table: HashTable) -> None:
    """Ищет запись через консольный ввод."""
    key = read_key_from_console()
    value = hash_table.read(key)
    print("Найдено:", normalize_key(key), "->", value)


def update_record_from_console(hash_table: HashTable) -> None:
    """Изменяет запись через консольный ввод."""
    key = read_key_from_console()
    value = read_value_from_console()
    hash_table.update(key, value)
    print("Запись изменена")


def delete_record_from_console(hash_table: HashTable) -> None:
    """Удаляет запись через консольный ввод."""
    key = read_key_from_console()
    hash_table.delete(key)
    print("Запись удалена")


def print_all_lab_results(hash_table: HashTable) -> None:
    """Печатает полный набор результатов для защиты лабораторной."""
    hash_table.print_hash_values()
    hash_table.print_table()
    hash_table.print_avl_structures()
    print_statistics(hash_table)


def process_menu_choice(hash_table: HashTable, choice: str) -> bool:
    """Обрабатывает выбранный пункт меню. Возвращает False для выхода."""
    try:
        if choice == "1":
            hash_table.print_hash_values()
        elif choice == "2":
            hash_table.print_table()
        elif choice == "3":
            add_record_from_console(hash_table)
        elif choice == "4":
            find_record_from_console(hash_table)
        elif choice == "5":
            update_record_from_console(hash_table)
        elif choice == "6":
            delete_record_from_console(hash_table)
        elif choice == "7":
            print_statistics(hash_table)
        elif choice == "8":
            demonstrate_crud(hash_table)
        elif choice == "9":
            print_all_lab_results(hash_table)
        elif choice == "10":
            run_unit_tests_from_menu()
        elif choice == "11":
            run_coverage_check_from_menu()
        elif choice == "12":
            hash_table.print_avl_structures()
        elif choice == "0":
            print("Выход из программы")
            return False
        else:
            print("Неверный пункт меню")
    except (ValueError, DuplicateKeyError, KeyNotFoundError) as error:
        print("Ошибка:", error)

    return True


def run_menu(hash_table: HashTable) -> None:
    """Запускает интерактивное меню."""
    should_continue = True

    while should_continue:
        print_menu()
        user_choice = input("Выберите пункт меню: ").strip()
        should_continue = process_menu_choice(hash_table, user_choice)


def main() -> None:
    """Точка входа в программу."""
    hash_table = build_default_hash_table()
    print("Лабораторная работа №4. Хеш-таблица. Вариант 6.")
    print("При запуске таблица уже заполнена демонстрационными данными по теме 'Литература'.")
    run_menu(hash_table)


if __name__ == "__main__":
    main()
