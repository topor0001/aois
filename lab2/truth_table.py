"""Truth table."""

from typing import List, Tuple


class TruthTable:
    def __init__(self, variables: List[str], table: List[Tuple[Tuple[int, ...], int]]):
        self._variables = variables
        self._table = table
        self._n = len(variables)
        self._value_map = {values: res for values, res in table}
    
    @property
    def variables(self) -> List[str]:
        return self._variables
    
    @property
    def table(self) -> List[Tuple[Tuple[int, ...], int]]:
        return self._table
    
    @property
    def n(self) -> int:
        return self._n
    
    def get_vector(self) -> str:
        return ''.join(str(res) for _, res in self._table)
    
    def get_ones_indices(self) -> List[int]:
        indices = []
        for values, res in self._table:
            if res == 1:
                indices.append(self._values_to_index(values))
        return indices
    
    def get_zeros_indices(self) -> List[int]:
        indices = []
        for values, res in self._table:
            if res == 0:
                indices.append(self._values_to_index(values))
        return indices
    
    def _values_to_index(self, values: Tuple[int, ...]) -> int:
        index = 0
        for i, val in enumerate(values):
            index |= val << (self._n - i - 1)
        return index
    
    @staticmethod
    def index_to_values(index: int, n: int) -> Tuple[int, ...]:
        values = []
        for i in range(n):
            bit = (index >> (n - i - 1)) & 1
            values.append(bit)
        return tuple(values)
    
    def get_value(self, values: Tuple[int, ...]) -> int:
        return self._value_map.get(values, 0)
    
    def is_const_zero(self) -> bool:
        return all(res == 0 for _, res in self._table)
    
    def is_const_one(self) -> bool:
        return all(res == 1 for _, res in self._table)