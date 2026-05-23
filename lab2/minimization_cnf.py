"""Минимизация КНФ через двойственную функцию."""

from typing import List, Tuple
from truth_table import TruthTable
from minimization_dnf import MinimizationDNF


class MinimizationCNF:
    def __init__(self, truth_table: TruthTable):
        self._table = truth_table
        self._variables = truth_table.variables
        self._n = truth_table.n
        self._zeros = truth_table.get_zeros_indices()

    def minimize_with_stages(self) -> Tuple[str, List[str]]:
        if not self._zeros:
            return '1', ["Функция тождественно равна 1"]
        if len(self._zeros) == (1 << self._n):
            return '0', ["Функция тождественно равна 0"]

        stages = [
            "Минимизация КНФ через двойственную функцию:",
            "  f*(x) = ¬f(¬x)",
            "  Сначала минимизируем ДНФ двойственной функции, затем применяем принцип двойственности."
        ]

        dual_table = self._build_dual_table()
        dnf_minimizer = MinimizationDNF(dual_table)
        dual_dnf, dnf_stages = dnf_minimizer.minimize_with_stages()

        stages.append("ДНФ двойственной функции:")
        for stage in dnf_stages:
            stages.append(f"  {stage}")

        cnf_result = self._dual_dnf_to_cnf(dual_dnf)
        stages.append(f"Итоговая минимизированная КНФ: {cnf_result}")
        return cnf_result, stages

    def _build_dual_table(self) -> TruthTable:
        dual_table_data = []
        for values, res in self._table.table:
            neg_values = tuple(1 - v for v in values)
            dual_res = 1 - res
            dual_table_data.append((neg_values, dual_res))
        dual_table_data.sort(key=lambda item: self._values_to_index(item[0]))
        return TruthTable(self._variables, dual_table_data)

    def _dual_dnf_to_cnf(self, dual_dnf: str) -> str:
        """Преобразует ДНФ двойственной функции в КНФ исходной функции.

        По принципу двойственности операции AND/OR меняются местами,
        но сами литералы не инвертируются. Например, двойственная ДНФ
        a&!b | c переходит в КНФ (a|!b)&c.
        """
        if dual_dnf == '0':
            return '1'
        if dual_dnf == '1':
            return '0'

        clauses = []
        for raw_term in dual_dnf.split('|'):
            term = raw_term.strip().strip('()')
            literals = [part.strip() for part in term.split('&') if part.strip()]
            clause = ' | '.join(literals)
            if len(literals) > 1:
                clause = '(' + clause + ')'
            clauses.append(clause)

        return ' & '.join(clauses) if clauses else '1'

    def _values_to_index(self, values: Tuple[int, ...]) -> int:
        index = 0
        for i, val in enumerate(values):
            index |= val << (self._n - i - 1)
        return index

    def get_dual_function(self) -> TruthTable:
        return self._build_dual_table()
