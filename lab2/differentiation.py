"""Boolean differentiation."""

from typing import List, Tuple, Dict
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
            neg_values = list(values)
            neg_values[var_idx] = 1 - neg_values[var_idx]
            neg_values_tuple = tuple(neg_values)
            derivative = self._value_map[values] ^ self._value_map[neg_values_tuple]
            result[values] = derivative
        
        return result
    
    def mixed(self, var_list: List[str]) -> Dict[Tuple[int, ...], int]:
        indices = [self._variables.index(v) for v in var_list]
        result = {}
        
        for values in self._value_map:
            current = self._value_map[values]
            
            for mask in range(1, 1 << len(indices)):
                neg_values = list(values)
                bits = 0
                
                for j, idx in enumerate(indices):
                    if mask >> j & 1:
                        neg_values[idx] = 1 - neg_values[idx]
                        bits += 1
                
                neg_tuple = tuple(neg_values)
                if bits % 2 == 1:
                    current ^= self._value_map[neg_tuple]
            
            result[values] = current
        
        return result
    
    def format_result(self, derivative: Dict[Tuple[int, ...], int]) -> List[str]:
        lines = []
        for values, res in sorted(derivative.items()):
            values_str = ''.join(str(v) for v in values)
            lines.append(f"  {values_str}: {res}")
        return lines
    
    def partial_vector(self, var: str) -> List[int]:
        """Return partial derivative as vector."""
        result = self.partial(var)
        n = self._n
        vector = []
        for i in range(1 << n):
            values = TruthTable.index_to_values(i, n)
            vector.append(result.get(values, 0))
        return vector