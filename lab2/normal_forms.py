"""SDNF and SKNF forms."""

from typing import List, Tuple
from truth_table import TruthTable


class NormalForms:
    def __init__(self, truth_table: TruthTable):
        self._table = truth_table
        self._variables = truth_table.variables
        self._n = truth_table.n
    
    def get_sdnf(self) -> Tuple[str, List[int]]:
        ones = self._table.get_ones_indices()
        
        if not ones:
            return '0', ones
        
        terms = []
        for idx in ones:
            values = TruthTable.index_to_values(idx, self._n)
            term_parts = []
            for var, val in zip(self._variables, values):
                if val == 0:
                    term_parts.append(f'!{var}')
                else:
                    term_parts.append(var)
            terms.append('(' + '&'.join(term_parts) + ')')
        
        return ' | '.join(terms), ones
    
    def get_sknf(self) -> Tuple[str, List[int]]:
        zeros = self._table.get_zeros_indices()
        
        if not zeros:
            return '1', zeros
        
        terms = []
        for idx in zeros:
            values = TruthTable.index_to_values(idx, self._n)
            term_parts = []
            for var, val in zip(self._variables, values):
                if val == 0:
                    term_parts.append(var)
                else:
                    term_parts.append(f'!{var}')
            terms.append('(' + '|'.join(term_parts) + ')')
        
        return ' & '.join(terms), zeros
    
    def get_index_form(self) -> str:
        return self._table.get_vector()
    
    def get_sdnf_numeric(self) -> List[int]:
        """Return SDNF numeric form."""
        return self._table.get_ones_indices()
    
    def get_sknf_numeric(self) -> List[int]:
        """Return SKNF numeric form."""
        return self._table.get_zeros_indices()