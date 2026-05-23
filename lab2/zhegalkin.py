"""Zhegalkin polynomial."""

from typing import List, Tuple
from truth_table import TruthTable


class ZhegalkinPolynomial:
    def __init__(self, truth_table: TruthTable):
        self._table = truth_table
        self._variables = truth_table.variables
        self._n = truth_table.n
        self._value_map = {values: res for values, res in truth_table.table}
    
    def compute(self) -> str:
        if self._table.is_const_zero():
            return '0'
        if self._table.is_const_one():
            return '1'
        
        coefficients = self._compute_coefficients()
        terms = []
        
        for mask in range(1 << self._n):
            if coefficients[mask] == 1:
                if mask == 0:
                    terms.append('1')
                else:
                    term_parts = []
                    for i in range(self._n):
                        if mask >> (self._n - i - 1) & 1:
                            term_parts.append(self._variables[i])
                    terms.append('&'.join(term_parts))
        
        if not terms:
            return '0'
        return ' XOR '.join(terms)
    
    def _compute_coefficients(self) -> List[int]:
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
    
    def get_coefficients(self) -> List[int]:
        """Return Zhegalkin coefficients."""
        return self._compute_coefficients()