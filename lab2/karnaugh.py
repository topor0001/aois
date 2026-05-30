"""Минимизация булевой функции методом карт Карно.

Поддерживаются функции до пяти переменных.
Для 5 переменных карта Карно выводится как две карты 4x4:
первый слой при первой переменной = 0,
второй слой при первой переменной = 1.
"""

from itertools import combinations, product
from typing import Iterable, List, Sequence, Set, Tuple

from truth_table import TruthTable

MAX_KARNAUGH_VARS = 5

Cell = Tuple[int, int]
Mask = Tuple[int, ...]
Rectangle = Set[Cell]


class KarnaughMap:
    """Карта Карно для ДНФ и КНФ."""

    def __init__(self, truth_table: TruthTable):
        if truth_table.n > MAX_KARNAUGH_VARS:
            raise ValueError(
                f"Карта Карно поддерживает не более {MAX_KARNAUGH_VARS} переменных."
            )

        self._table = truth_table
        self._variables = truth_table.variables
        self._n = truth_table.n
        self._value_map = {values: res for values, res in truth_table.table}

    def minimize_dnf(self) -> Tuple[str, List[str]]:
        """Возвращает минимизированную ДНФ и строки с картой Карно."""
        if self._table.is_const_zero():
            return "0", self._format_const_map("все значения равны 0")
        if self._table.is_const_one():
            return "1", self._format_const_map("все значения равны 1")

        result, explanation = self._minimize_by_target(target=1, form="dnf")
        return result, explanation

    def minimize_cnf(self) -> Tuple[str, List[str]]:
        """Возвращает минимизированную КНФ и строки с картой Карно."""
        if self._table.is_const_zero():
            return "0", self._format_const_map("все значения равны 0")
        if self._table.is_const_one():
            return "1", self._format_const_map("все значения равны 1")

        result, explanation = self._minimize_by_target(target=0, form="cnf")
        return result, explanation

    def get_karnaugh_map(self, target: int = 1) -> List[List[int]]:
        """Возвращает двумерную карту для 1-4 переменных.

        Для 5 переменных возвращает первую карту-слой.
        Полный вывод двух слоёв используется в minimize_dnf/minimize_cnf.
        """
        if self._n == 5:
            maps, _, _ = self._build_5var_maps(target)
            return maps[0]

        k_map, _, _ = self._build_map(target)
        return k_map

    def _minimize_by_target(self, target: int, form: str) -> Tuple[str, List[str]]:
        if self._n == 5:
            masks = self._get_all_valid_masks(target)
            selected = self._select_minimal_cover(masks, target)
            expression = self._masks_to_expression(selected, form)
            lines = self._format_5var_maps(target)
            lines.extend(self._format_selected_groups(selected, form))
            return expression, lines

        k_map, row_labels, col_labels = self._build_map(target)
        rectangles = self._get_all_valid_rectangles(k_map, target)
        masks = self._rectangles_to_unique_masks(rectangles, row_labels, col_labels)
        selected = self._select_minimal_cover(masks, target)
        expression = self._masks_to_expression(selected, form)
        lines = self._format_map(k_map, row_labels, col_labels, target)
        lines.extend(self._format_selected_groups(selected, form))
        return expression, lines

    def _build_map(self, target: int) -> Tuple[List[List[int]], List[int], List[int]]:
        rows, cols = self._map_size()
        row_labels = self._gray_labels(rows)
        col_labels = self._gray_labels(cols)
        k_map = [[0 for _ in range(cols)] for _ in range(rows)]

        for values, result in self._value_map.items():
            if result == target:
                row_value, col_value = self._values_to_row_col(values)
                row_index = row_labels.index(row_value)
                col_index = col_labels.index(col_value)
                k_map[row_index][col_index] = 1

        return k_map, row_labels, col_labels

    def _build_5var_maps(self, target: int) -> Tuple[List[List[List[int]]], List[int], List[int]]:
        row_labels = self._gray_labels(4)
        col_labels = self._gray_labels(4)

        maps = [
            [[0 for _ in range(4)] for _ in range(4)],
            [[0 for _ in range(4)] for _ in range(4)]
        ]

        for values, result in self._value_map.items():
            if result == target:
                layer = values[0]
                row_value = self._bits_to_int(values[1:3])
                col_value = self._bits_to_int(values[3:5])

                row_index = row_labels.index(row_value)
                col_index = col_labels.index(col_value)

                maps[layer][row_index][col_index] = 1

        return maps, row_labels, col_labels

    def _map_size(self) -> Tuple[int, int]:
        if self._n == 1:
            return 1, 2
        if self._n == 2:
            return 2, 2
        if self._n == 3:
            return 2, 4
        return 4, 4

    @staticmethod
    def _gray_labels(count: int) -> List[int]:
        return [index ^ (index >> 1) for index in range(count)]

    def _values_to_row_col(self, values: Tuple[int, ...]) -> Tuple[int, int]:
        row_bits_count = 0 if self._n == 1 else self._n // 2
        row_value = self._bits_to_int(values[:row_bits_count])
        col_value = self._bits_to_int(values[row_bits_count:])
        return row_value, col_value

    @staticmethod
    def _bits_to_int(bits: Sequence[int]) -> int:
        value = 0
        for bit in bits:
            value = (value << 1) | bit
        return value

    def _cell_to_values(
        self,
        cell: Cell,
        row_labels: List[int],
        col_labels: List[int],
    ) -> Tuple[int, ...]:
        row_index, col_index = cell
        row_bits_count = 0 if self._n == 1 else self._n // 2
        col_bits_count = self._n - row_bits_count

        row_bits = self._int_to_bits(row_labels[row_index], row_bits_count)
        col_bits = self._int_to_bits(col_labels[col_index], col_bits_count)

        return tuple(row_bits + col_bits)

    @staticmethod
    def _int_to_bits(value: int, bits_count: int) -> List[int]:
        return [(value >> shift) & 1 for shift in range(bits_count - 1, -1, -1)]

    def _get_all_valid_rectangles(self, k_map: List[List[int]], target: int) -> List[Rectangle]:
        rows = len(k_map)
        cols = len(k_map[0])
        rectangles: Set[frozenset[Cell]] = set()

        for height in self._powers_of_two(rows):
            for width in self._powers_of_two(cols):
                rectangles.update(
                    self._rectangles_of_size(k_map, target, height, width)
                )

        return [set(rectangle) for rectangle in rectangles]

    @staticmethod
    def _powers_of_two(limit: int) -> List[int]:
        values = []
        size = 1

        while size <= limit:
            values.append(size)
            size *= 2

        return values

    def _rectangles_of_size(
        self,
        k_map: List[List[int]],
        target: int,
        height: int,
        width: int,
    ) -> Set[frozenset[Cell]]:
        rows = len(k_map)
        cols = len(k_map[0])
        found: Set[frozenset[Cell]] = set()

        for row in range(rows):
            for col in range(cols):
                cells = self._rectangle_cells(row, col, height, width, rows, cols)

                if all(k_map[r][c] == 1 for r, c in cells):
                    found.add(frozenset(cells))

        return found

    @staticmethod
    def _rectangle_cells(
        row: int,
        col: int,
        height: int,
        width: int,
        rows: int,
        cols: int,
    ) -> Rectangle:
        return {
            ((row + row_delta) % rows, (col + col_delta) % cols)
            for row_delta in range(height)
            for col_delta in range(width)
        }

    def _rectangles_to_unique_masks(
        self,
        rectangles: Iterable[Rectangle],
        row_labels: List[int],
        col_labels: List[int],
    ) -> List[Mask]:
        masks = {
            self._values_group_to_mask(
                [
                    self._cell_to_values(cell, row_labels, col_labels)
                    for cell in rectangle
                ]
            )
            for rectangle in rectangles
        }

        return sorted(masks, key=lambda mask: (self._literal_count(mask), mask))

    @staticmethod
    def _values_group_to_mask(values_group: List[Tuple[int, ...]]) -> Mask:
        mask = []

        for position in range(len(values_group[0])):
            bits = {values[position] for values in values_group}
            mask.append(bits.pop() if len(bits) == 1 else -1)

        return tuple(mask)

    def _get_all_valid_masks(self, target: int) -> List[Mask]:
        masks = []

        for mask in product([-1, 0, 1], repeat=self._n):
            covered_values = [
                values
                for values, result in self._table.table
                if self._covers(mask, values)
            ]

            if not covered_values:
                continue

            if all(self._value_map[values] == target for values in covered_values):
                masks.append(tuple(mask))

        masks = list(set(masks))
        masks.sort(key=lambda item: (self._literal_count(item), item))

        return masks

    def _select_minimal_cover(self, masks: List[Mask], target: int) -> List[Mask]:
        target_values = [
            values
            for values, result in self._table.table
            if result == target
        ]

        coverage = {
            mask: {
                values
                for values in target_values
                if self._covers(mask, values)
            }
            for mask in masks
        }

        target_set = set(target_values)
        best_combo: Tuple[Mask, ...] | None = None
        best_score: Tuple[int, int] | None = None

        for size in range(1, len(masks) + 1):
            for combo in combinations(masks, size):
                covered = set().union(*(coverage[mask] for mask in combo))

                if covered == target_set:
                    score = (
                        len(combo),
                        sum(self._literal_count(mask) for mask in combo)
                    )

                    if best_score is None or score < best_score:
                        best_combo = combo
                        best_score = score

            if best_combo is not None:
                break

        return list(best_combo) if best_combo else []

    @staticmethod
    def _covers(mask: Mask, values: Tuple[int, ...]) -> bool:
        return all(
            mask_bit == -1 or mask_bit == value
            for mask_bit, value in zip(mask, values)
        )

    @staticmethod
    def _literal_count(mask: Mask) -> int:
        return sum(1 for value in mask if value != -1)

    def _masks_to_expression(self, masks: List[Mask], form: str) -> str:
        if not masks:
            return "0" if form == "dnf" else "1"

        terms = [
            self._mask_to_dnf_term(mask)
            if form == "dnf"
            else self._mask_to_cnf_clause(mask)
            for mask in masks
        ]

        return (" | " if form == "dnf" else " & ").join(terms)

    def _mask_to_dnf_term(self, mask: Mask) -> str:
        parts = [
            var if bit == 1 else f"!{var}"
            for var, bit in zip(self._variables, mask)
            if bit != -1
        ]

        return self._join_parts(parts, "&", empty="1")

    def _mask_to_cnf_clause(self, mask: Mask) -> str:
        parts = [
            var if bit == 0 else f"!{var}"
            for var, bit in zip(self._variables, mask)
            if bit != -1
        ]

        return self._join_parts(parts, "|", empty="0")

    @staticmethod
    def _join_parts(parts: List[str], separator: str, empty: str) -> str:
        if not parts:
            return empty

        text = separator.join(parts)

        return f"({text})" if len(parts) > 1 else text

    def _format_map(
        self,
        k_map: List[List[int]],
        row_labels: List[int],
        col_labels: List[int],
        target: int,
    ) -> List[str]:
        row_name, col_name = self._axis_names()

        lines = [
            f"Карта Карно для {'единиц' if target == 1 else 'нулей'}:"
        ]

        header_cells = [
            self._label_to_binary(label, len(col_name)).rjust(4)
            for label in col_labels
        ]

        lines.append(f"{row_name}\\{col_name}".ljust(8) + " ".join(header_cells))

        for row_index, row in enumerate(k_map):
            row_label = self._label_to_binary(
                row_labels[row_index],
                len(row_name)
            ).rjust(6)

            lines.append(
                row_label + " | " + " ".join(str(value).rjust(4) for value in row)
            )

        return lines

    def _format_5var_maps(self, target: int) -> List[str]:
        maps, row_labels, col_labels = self._build_5var_maps(target)

        layer_var = self._variables[0]
        row_name = "".join(self._variables[1:3])
        col_name = "".join(self._variables[3:5])

        lines = [
            f"Карта Карно для {'единиц' if target == 1 else 'нулей'}:"
        ]

        for layer_value, k_map in enumerate(maps):
            lines.append(f"Слой {layer_var}={layer_value}:")

            header_cells = [
                self._label_to_binary(label, len(col_name)).rjust(4)
                for label in col_labels
            ]

            lines.append(f"{row_name}\\{col_name}".ljust(8) + " ".join(header_cells))

            for row_index, row in enumerate(k_map):
                row_label = self._label_to_binary(
                    row_labels[row_index],
                    len(row_name)
                ).rjust(6)

                lines.append(
                    row_label + " | " + " ".join(str(value).rjust(4) for value in row)
                )

        return lines

    def _axis_names(self) -> Tuple[str, str]:
        if self._n == 1:
            return "-", self._variables[0]

        row_vars_count = self._n // 2

        return (
            "".join(self._variables[:row_vars_count]),
            "".join(self._variables[row_vars_count:])
        )

    @staticmethod
    def _label_to_binary(label: int, width: int) -> str:
        return "-" if width == 0 else format(label, f"0{width}b")

    def _format_selected_groups(self, masks: List[Mask], form: str) -> List[str]:
        title = "Выбранные области карты Карно:"

        terms = [
            self._mask_to_dnf_term(mask)
            if form == "dnf"
            else self._mask_to_cnf_clause(mask)
            for mask in masks
        ]

        return [title, f"  {terms}"]

    def _format_const_map(self, comment: str) -> List[str]:
        if self._n == 5:
            target = 1 if self._table.is_const_one() else 0
            lines = self._format_5var_maps(target)
            lines.append(f"Особый случай: {comment}.")
            return lines

        target = 1 if self._table.is_const_one() else 0
        k_map, row_labels, col_labels = self._build_map(target)
        lines = self._format_map(k_map, row_labels, col_labels, target)
        lines.append(f"Особый случай: {comment}.")
        return lines
