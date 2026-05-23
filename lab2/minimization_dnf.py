"""Минимизация ДНФ расчётным и расчётно-табличным методом."""

from itertools import combinations
from typing import List, Tuple, Set
from truth_table import TruthTable
from implicant import Implicant


class MinimizationDNF:
    def __init__(self, truth_table: TruthTable):
        self._table = truth_table
        self._variables = truth_table.variables
        self._n = truth_table.n
        self._ones = truth_table.get_ones_indices()

    def minimize_with_stages(self) -> Tuple[str, List[str]]:
        if not self._ones:
            return '0', ["Функция тождественно равна 0"]

        if len(self._ones) == (1 << self._n):
            return '1', ["Функция тождественно равна 1"]

        stages = []
        current = self._get_initial_implicants()
        stages.append(self._format_initial_stage(current))

        all_prime, gluing_stages = self._perform_skleivanie(current)
        stages.extend(gluing_stages)

        if not all_prime:
            return '0', stages

        prime_list, minterms, coverage = self._build_coverage_table(all_prime)
        stages.extend(self._format_coverage_table(prime_list, minterms, coverage))

        selected = self._solve_coverage(prime_list, minterms, coverage)
        stages.append(self._format_selected_stage(selected))

        result = ' | '.join(imp.to_string() for imp in selected) if selected else '0'
        stages.append(f"Итоговая минимизированная ДНФ: {result}")
        return result, stages

    def _get_initial_implicants(self) -> Set[Implicant]:
        result = set()
        for idx in self._ones:
            binary = TruthTable.index_to_values(idx, self._n)
            result.add(Implicant.from_binary(binary, self._variables))
        return result

    def _format_initial_stage(self, implicants: Set[Implicant]) -> str:
        terms = [imp.to_string() for imp in sorted(implicants, key=lambda x: x.mask)]
        return f"Исходные конституэнты СДНФ: {terms}"

    def _perform_skleivanie(self, current: Set[Implicant]) -> Tuple[Set[Implicant], List[str]]:
        stages = []
        all_prime = set()
        stage_num = 1

        while current:
            used = set()
            next_level = set()
            current_list = sorted(list(current), key=lambda x: x.mask)
            pairs = []

            for i in range(len(current_list)):
                for j in range(i + 1, len(current_list)):
                    combined = Implicant.combine(current_list[i], current_list[j])
                    if combined:
                        next_level.add(combined)
                        used.add(current_list[i])
                        used.add(current_list[j])
                        pairs.append((current_list[i], current_list[j], combined))

            if pairs:
                stages.append(f"Этап склеивания {stage_num}:")
                for left, right, combined in pairs:
                    stages.append(f"  {left.to_string()} ∨ {right.to_string()} => {combined.to_string()}")
                unique = [imp.to_string() for imp in sorted(next_level, key=lambda x: x.mask)]
                stages.append(f"  Результат этапа: {unique}")

            for imp in current:
                if imp not in used:
                    all_prime.add(imp)

            current = next_level
            stage_num += 1

        if all_prime:
            primes = [imp.to_string() for imp in sorted(all_prime, key=lambda x: x.mask)]
            stages.append(f"Простые импликанты: {primes}")

        return all_prime, stages

    def _build_coverage_table(
        self,
        primes: Set[Implicant],
    ) -> Tuple[List[Implicant], List[Tuple[int, ...]], List[List[bool]]]:
        prime_list = sorted(list(primes), key=lambda x: (x.size(), x.mask))
        minterms = [TruthTable.index_to_values(idx, self._n) for idx in self._ones]
        coverage = []
        for imp in prime_list:
            coverage.append([imp.covers(minterm) for minterm in minterms])
        return prime_list, minterms, coverage

    def _format_coverage_table(
        self,
        primes: List[Implicant],
        minterms: List[Tuple[int, ...]],
        coverage: List[List[bool]],
    ) -> List[str]:
        stages = ["Таблица покрытия:"]
        indices = [self._values_to_index(m) for m in minterms]
        header = "Импликанта ".ljust(14) + "".join(f"m{idx:<4}" for idx in indices)
        stages.append(header)
        for i, imp in enumerate(primes):
            row = imp.to_string().ljust(14)
            for j in range(len(minterms)):
                row += "  X  " if coverage[i][j] else "     "
            stages.append(row)
        return stages

    def _solve_coverage(
        self,
        primes: List[Implicant],
        minterms: List[Tuple[int, ...]],
        coverage: List[List[bool]],
    ) -> List[Implicant]:
        if not minterms:
            return []

        uncovered = set(range(len(minterms)))
        selected = set()

        # 1. Существенные простые импликанты.
        changed = True
        while changed:
            changed = False
            for m_idx in list(uncovered):
                covering = [p_idx for p_idx in range(len(primes)) if coverage[p_idx][m_idx]]
                if len(covering) == 1:
                    p_idx = covering[0]
                    if p_idx not in selected:
                        selected.add(p_idx)
                        changed = True
                    for col in range(len(minterms)):
                        if coverage[p_idx][col]:
                            uncovered.discard(col)

        if not uncovered:
            return [primes[i] for i in sorted(selected, key=lambda idx: primes[idx].mask)]

        # 2. Полный перебор оставшегося покрытия. Для <= 5 переменных это быстро и даёт точный минимум.
        candidate_indices = [i for i in range(len(primes)) if i not in selected]
        best_combo = None
        best_score = None

        for r in range(1, len(candidate_indices) + 1):
            for combo in combinations(candidate_indices, r):
                covered = set()
                for p_idx in combo:
                    for m_idx in uncovered:
                        if coverage[p_idx][m_idx]:
                            covered.add(m_idx)
                if covered >= uncovered:
                    literals_count = sum(primes[p_idx].size() for p_idx in combo)
                    score = (r, literals_count)
                    if best_score is None or score < best_score:
                        best_score = score
                        best_combo = combo
            if best_combo is not None:
                break

        if best_combo:
            selected.update(best_combo)

        return [primes[i] for i in sorted(selected, key=lambda idx: primes[idx].mask)]

    def _format_selected_stage(self, selected: List[Implicant]) -> str:
        return f"Выбранное минимальное покрытие: {[imp.to_string() for imp in selected]}"

    def _values_to_index(self, values: Tuple[int, ...]) -> int:
        index = 0
        for i, val in enumerate(values):
            index |= val << (self._n - i - 1)
        return index

    def get_prime_implicants(self) -> List[Implicant]:
        current = self._get_initial_implicants()
        all_prime, _ = self._perform_skleivanie(current)
        return sorted(list(all_prime), key=lambda x: x.mask)
