"""
Unit-тесты для лабораторной работы №4.
Запуск:
python tests.py
"""

from main import (
    AvlNode,
    DuplicateKeyError,
    HashTable,
    KeyNotFoundError,
    balance_node,
    build_default_hash_table,
    build_default_literature_records,
    calculate_hash_address,
    calculate_numeric_value,
    count_avl_nodes,
    delete_avl_node,
    find_avl_node,
    find_min_node,
    format_avl_node,
    print_avl_tree,
    demonstrate_crud,
    get_balance_factor,
    get_height,
    get_letter_index,
    insert_avl_node,
    normalize_key,
    print_all_lab_results,
    print_statistics,
    rotate_left,
    rotate_right,
    traverse_avl,
    update_height,
    validate_lab_requirements,
)


PASSED_TESTS = 0


def check(condition, message):
    global PASSED_TESTS

    if not condition:
        raise AssertionError(message)

    PASSED_TESTS += 1


def test_normalize_key():
    check(normalize_key(" роман ") == "РОМАН", "Ошибка normalize_key")


def test_get_letter_index():
    check(get_letter_index("А") == 0, "Ошибка индекса буквы А")
    check(get_letter_index("Б") == 1, "Ошибка индекса буквы Б")


def test_calculate_numeric_value():
    expected_value = get_letter_index("Р") * 33 + get_letter_index("О")
    check(calculate_numeric_value("Роман") == expected_value, "Ошибка V")


def test_calculate_hash_address():
    expected_hash = calculate_numeric_value("Роман") % 20
    check(calculate_hash_address("Роман") == expected_hash, "Ошибка h")


def test_avl_insert_find_count():
    root = None
    root = insert_avl_node(root, "РОМАН", "данные", 1, 1)
    root = insert_avl_node(root, "РОМАНТИЗМ", "данные", 1, 1)

    check(find_avl_node(root, "РОМАН") is not None, "Узел не найден")
    check(count_avl_nodes(root) == 2, "Ошибка подсчета узлов")


def test_duplicate_avl_key():
    root = None
    root = insert_avl_node(root, "ПОЭТ", "данные", 1, 1)

    try:
        insert_avl_node(root, "ПОЭТ", "данные", 1, 1)
    except DuplicateKeyError:
        check(True, "Дубликат обработан")
        return

    raise AssertionError("Дубликат не был обработан")


def test_avl_delete():
    root = None
    root = insert_avl_node(root, "А", "1", 1, 1)
    root = insert_avl_node(root, "Б", "2", 1, 1)
    root = delete_avl_node(root, "А")

    check(find_avl_node(root, "А") is None, "Удаление AVL не работает")


def test_avl_delete_missing():
    try:
        delete_avl_node(None, "А")
    except KeyNotFoundError:
        check(True, "Удаление отсутствующего ключа обработано")
        return

    raise AssertionError("Не обработано удаление отсутствующего ключа")


def test_avl_traverse():
    root = None
    root = insert_avl_node(root, "Б", "2", 1, 1)
    root = insert_avl_node(root, "А", "1", 1, 1)

    keys = [node.key for node in traverse_avl(root)]
    check(keys == ["А", "Б"], "Обход AVL работает неверно")


def test_avl_helpers():
    node = AvlNode("А", "1", 1, 1)
    update_height(node)

    check(get_height(node) == 1, "Ошибка высоты")
    check(get_balance_factor(node) == 0, "Ошибка баланс-фактора")
    check(balance_node(node).key == "А", "Ошибка balance_node")


def test_rotations():
    root = AvlNode("В", "3", 1, 1)
    root.left = AvlNode("Б", "2", 1, 1)
    root.left.left = AvlNode("А", "1", 1, 1)

    update_height(root.left)
    update_height(root)

    rotated = rotate_right(root)
    check(rotated.key == "Б", "Правый поворот неверен")

    second_root = AvlNode("А", "1", 1, 1)
    second_root.right = AvlNode("Б", "2", 1, 1)
    second_root.right.right = AvlNode("В", "3", 1, 1)

    update_height(second_root.right)
    update_height(second_root)

    second_rotated = rotate_left(second_root)
    check(second_rotated.key == "Б", "Левый поворот неверен")


def test_hash_table_create_read_update_delete():
    table = HashTable()

    table.create("Роман", "старое значение")
    check(table.read("Роман") == "старое значение", "CREATE/READ не работает")

    table.update("Роман", "новое значение")
    check(table.read("Роман") == "новое значение", "UPDATE не работает")

    table.delete("Роман")

    try:
        table.read("Роман")
    except KeyNotFoundError:
        check(True, "DELETE обработан")
        return

    raise AssertionError("DELETE не работает")


def test_hash_table_duplicate_key():
    table = HashTable()
    table.create("Поэт", "данные")

    try:
        table.create("Поэт", "другие данные")
    except DuplicateKeyError:
        check(True, "Дубликат в таблице обработан")
        return

    raise AssertionError("Дубликат в таблице не обработан")


def test_missing_key_read_and_update():
    table = HashTable()

    check(table.read("Роман", raise_error=False) is None, "read без ошибки неверен")

    try:
        table.update("Роман", "значение")
    except KeyNotFoundError:
        check(True, "update отсутствующего ключа обработан")
        return

    raise AssertionError("update отсутствующего ключа не обработан")


def test_default_records_count():
    records = build_default_literature_records()
    check(len(records) >= 10, "Недостаточно исходных записей")


def test_lab_requirements():
    table = build_default_hash_table()

    check(table.size >= 20, "Размер таблицы меньше 20")
    check(table.records_count >= 10, "Записей меньше 10")
    check(table.get_collision_count() >= 2, "Коллизий меньше 2")
    check(table.get_chain_records_count() >= 3, "Мало записей в цепочках")
    check(validate_lab_requirements(table), "Проверка требований не прошла")



def test_output_and_min_node_functions():
    table = build_default_hash_table()
    all_records = table.get_all_records()

    check(len(all_records) == table.records_count, "get_all_records неверен")

    bucket = None
    bucket = insert_avl_node(bucket, "Б", "2", 1, 1)
    bucket = insert_avl_node(bucket, "А", "1", 1, 1)

    check(find_min_node(bucket).key == "А", "find_min_node неверен")

    table.print_hash_values()
    table.print_table()
    table.print_avl_structures()
    print_avl_tree(bucket)
    formatted_tree = format_avl_node(bucket)
    check(any("height=" in line for line in formatted_tree), "Нет вывода высоты AVL")
    check(any("balance=" in line for line in formatted_tree), "Нет вывода баланса AVL")
    demonstrate_crud(table)
    check(table.read("Сатира", raise_error=False) is None, "CRUD delete неверен")

def test_load_factor():
    table = build_default_hash_table()
    expected = table.records_count / table.size

    check(table.get_load_factor() == expected, "Коэффициент заполнения неверен")


def test_print_result_helpers():
    table = build_default_hash_table()
    print_statistics(table)
    print_all_lab_results(table)
    check(validate_lab_requirements(table), "Печать результатов нарушила таблицу")


def run_all_tests():
    test_normalize_key()
    test_get_letter_index()
    test_calculate_numeric_value()
    test_calculate_hash_address()
    test_avl_insert_find_count()
    test_duplicate_avl_key()
    test_avl_delete()
    test_avl_delete_missing()
    test_avl_traverse()
    test_avl_helpers()
    test_rotations()
    test_hash_table_create_read_update_delete()
    test_hash_table_duplicate_key()
    test_missing_key_read_and_update()
    test_default_records_count()
    test_lab_requirements()
    test_output_and_min_node_functions()
    test_load_factor()
    test_print_result_helpers()

    print(f"Все unit-тесты пройдены: {PASSED_TESTS}")


if __name__ == "__main__":
    run_all_tests()
