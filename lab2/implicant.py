"""Implicant for minimization."""

from typing import List, Tuple, Optional, Set


class Implicant:
    def __init__(self, mask: Tuple[int, ...], variables: List[str]):
        self.mask = mask
        self._variables = variables
        self._n = len(mask)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Implicant):
            return False
        return self.mask == other.mask
    
    def __hash__(self) -> int:
        return hash(self.mask)
    
    def __lt__(self, other: 'Implicant') -> bool:
        return self.mask < other.mask
    
    def covers(self, binary: Tuple[int, ...]) -> bool:
        for i, val in enumerate(self.mask):
            if val != -1 and val != binary[i]:
                return False
        return True
    
    def to_string(self) -> str:
        parts = []
        for i, val in enumerate(self.mask):
            if val == 1:
                parts.append(self._variables[i])
            elif val == 0:
                parts.append(f'!{self._variables[i]}')
        
        if not parts:
            return '1'
        if len(parts) == 1:
            return parts[0]
        if len(parts) == 2:
            return '&'.join(parts)
        return '(' + '&'.join(parts) + ')'
    
    def size(self) -> int:
        return sum(1 for val in self.mask if val != -1)
    
    def get_mask(self) -> Tuple[int, ...]:
        return self.mask
    
    @staticmethod
    def can_combine(a: 'Implicant', b: 'Implicant') -> bool:
        diff_count = 0
        for i in range(len(a.mask)):
            if a.mask[i] != b.mask[i]:
                diff_count += 1
                if diff_count > 1:
                    return False
        return diff_count == 1
    
    @staticmethod
    def combine(a: 'Implicant', b: 'Implicant') -> Optional['Implicant']:
        if not Implicant.can_combine(a, b):
            return None
        
        new_mask = list(a.mask)
        for i in range(len(a.mask)):
            if a.mask[i] != b.mask[i]:
                new_mask[i] = -1
                break
        return Implicant(tuple(new_mask), a._variables)
    
    @staticmethod
    def from_binary(binary: Tuple[int, ...], variables: List[str]) -> 'Implicant':
        return Implicant(binary, variables)
    
    @staticmethod
    def from_string(term: str, variables: List[str]) -> 'Implicant':
        """Create implicant from string like 'a&!b' or 'a'."""
        mask = [-1] * len(variables)
        term = term.replace('(', '').replace(')', '')
        parts = term.split('&')
        for part in parts:
            part = part.strip()
            if part.startswith('!'):
                var = part[1]
                if var in variables:
                    idx = variables.index(var)
                    mask[idx] = 0
            else:
                if part in variables:
                    idx = variables.index(part)
                    mask[idx] = 1
        return Implicant(tuple(mask), variables)