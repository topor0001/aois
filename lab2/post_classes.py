"""Post classes T0, T1, S, M, L."""

from typing import List, Dict, Tuple
from truth_table import TruthTable


class PostClasses:
    def __init__(self, truth_table: TruthTable):
        self._table = truth_table
        self._variables = truth_table.variables
        self._n = truth_table.n
        self._value_map = {values: res for values, res in truth_table.table}
    
    def is_t0(self) -> bool:
        zero_vector = tuple([0] * self._n)
        return self._value_map.get(zero_vector, 0) == 0
    
    def is_t1(self) -> bool:
        one_vector = tuple([1] * self._n)
        return self._value_map.get(one_vector, 1) == 1
    
    def is_self_dual(self) -> bool:
        for values, res in self._value_map.items():
            neg_values = tuple(1 - v for v in values)
            neg_res = self._value_map.get(neg_values)
            if neg_res is None or neg_res != 1 - res:
                return False
        return True
    
    def is_monotonic(self) -> bool:
        values_list = list(self._value_map.keys())
        
        for i in range(len(values_list)):
            for j in range(i + 1, len(values_list)):
                v1 = values_list[i]
                v2 = values_list[j]
                r1 = self._value_map[v1]
                r2 = self._value_map[v2]
                
                if self._dominates(v1, v2) and r1 > r2:
                    return False
                if self._dominates(v2, v1) and r1 < r2:
                    return False
        return True
    
    def _dominates(self, a: Tuple[int, ...], b: Tuple[int, ...]) -> bool:
        return all(a[k] <= b[k] for k in range(self._n))
    
    def is_linear(self) -> bool:
        coefficients = self._compute_zhegalkin_coefficients()
        for mask in range(1 << self._n):
            if coefficients[mask] == 1 and bin(mask).count('1') > 1:
                return False
        return True
    
    def _compute_zhegalkin_coefficients(self) -> List[int]:
        size = 1 << self._n
        function = [0] * size
        
        for values, res in self._value_map.items():
            idx = self._values_to_index(values)
            function[idx] = res
        
        coefficients = function.copy()
        
        for i in range(self._n):
            step = 1 << i
            for j in range(size):
                if j & step:
                    coefficients[j] ^= coefficients[j ^ step]
        
        return coefficients
    
    def _values_to_index(self, values: Tuple[int, ...]) -> int:
        index = 0
        for i, val in enumerate(values):
            index |= val << (self._n - i - 1)
        return index
    
    def get_all(self) -> Dict[str, bool]:
        return {
            'T0 (preserves 0)': self.is_t0(),
            'T1 (preserves 1)': self.is_t1(),
            'S (self-dual)': self.is_self_dual(),
            'M (monotonic)': self.is_monotonic(),
            'L (linear)': self.is_linear(),
        }