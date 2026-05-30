from itertools import combinations
from typing import Dict, List, Tuple

from truth_table import TruthTable


class BooleanDerivative:
    def __init__(self, truth_table: TruthTable):
        self._table = truth_table
        self._variables = truth_table.variables
        self._n = truth_table.n
        self._value_map = {values: res for values, res in truth_table.table}

    def partial(self, var: str) -> Dict[Tuple[int, ...], int]:
        var_idx = self._variables.index(var)
        result = {}

        for values in self._value_map:
            changed_values = list(values)
            changed_values[var_idx] = 1 - changed_values[var_idx]
            changed_tuple = tuple(changed_values)

            result[values] = self._value_map[values] ^ self._value_map[changed_tuple]

        return result

    def mixed(self, var_list: List[str]) -> Dict[Tuple[int, ...], int]:
        indices = [self._variables.index(v) for v in var_list]
        result = {}

        for values in self._value_map:
            derivative = 0

            for mask in range(1 << len(indices)):
                changed_values = list(values)

                for j, idx in enumerate(indices):
                    if (mask >> j) & 1:
                        changed_values[idx] = 1 - changed_values[idx]

                derivative ^= self._value_map[tuple(changed_values)]

            result[values] = derivative

        return result

    def all_partial_derivatives(self) -> Dict[str, Dict[Tuple[int, ...], int]]:
        result = {}

        for var in self._variables:
            result[var] = self.partial(var)

        return result

    def all_mixed_derivatives(self) -> Dict[Tuple[str, ...], Dict[Tuple[int, ...], int]]:
        result = {}
        max_order = min(4, len(self._variables))

        for order in range(2, max_order + 1):
            for combo in combinations(self._variables, order):
                result[combo] = self.mixed(list(combo))

        return result

    def format_result(self, derivative: Dict[Tuple[int, ...], int]) -> List[str]:
        lines = []

        for values, res in sorted(derivative.items()):
            values_str = ''.join(str(v) for v in values)
            lines.append(f"  {values_str}: {res}")

        return lines

    def partial_vector(self, var: str) -> List[int]:
        result = self.partial(var)
        vector = []

        for i in range(1 << self._n):
            values = TruthTable.index_to_values(i, self._n)
            vector.append(result.get(values, 0))

        return vector

    def mixed_vector(self, var_list: List[str]) -> List[int]:
        result = self.mixed(var_list)
        vector = []

        for i in range(1 << self._n):
            values = TruthTable.index_to_values(i, self._n)
            vector.append(result.get(values, 0))

        return vector