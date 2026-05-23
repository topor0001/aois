"""Парсер булевых функций без использования eval()."""

from typing import Dict, List, Tuple
from constants import (
    MAX_VARIABLES, OPERATOR_PRIORITIES, UNARY_OPERATORS,
    BINARY_OPERATORS, TOKEN_VARIABLE, TOKEN_OPERATOR,
    TOKEN_LPAREN, TOKEN_RPAREN
)


class ParseError(Exception):
    pass


def _normalize_expression(expression: str) -> str:
    return (expression
            .replace(' ', '')
            .replace('¬', '!')
            .replace('∧', '&')
            .replace('∨', '|')
            .replace('→', '->'))


def tokenize(expression: str) -> List[Tuple[str, str]]:
    """Разбивает выражение на токены."""
    expression = _normalize_expression(expression)
    tokens = []
    index = 0
    length = len(expression)

    if not expression:
        raise ParseError("Пустое выражение")

    while index < length:
        char = expression[index]

        if char.isspace():
            index += 1
            continue

        if 'a' <= char <= 'e':
            tokens.append((TOKEN_VARIABLE, char))
            index += 1
            continue

        if char == '-' and index + 1 < length and expression[index + 1] == '>':
            tokens.append((TOKEN_OPERATOR, '->'))
            index += 2
            continue

        if char == '~':
            tokens.append((TOKEN_OPERATOR, '~'))
            index += 1
            continue

        if char in '!&|':
            tokens.append((TOKEN_OPERATOR, char))
            index += 1
            continue

        if char == '(':
            tokens.append((TOKEN_LPAREN, '('))
            index += 1
            continue

        if char == ')':
            tokens.append((TOKEN_RPAREN, ')'))
            index += 1
            continue

        raise ParseError(f"Недопустимый символ: {char}")

    return tokens


def _validate_token_sequence(tokens: List[Tuple[str, str]]) -> None:
    expect_operand = True
    balance = 0

    for token_type, token_value in tokens:
        if token_type == TOKEN_VARIABLE:
            if not expect_operand:
                raise ParseError("Пропущена операция между переменными")
            expect_operand = False
        elif token_type == TOKEN_OPERATOR:
            if token_value in UNARY_OPERATORS:
                if not expect_operand:
                    raise ParseError("Некорректное положение унарной операции")
            else:
                if expect_operand:
                    raise ParseError("Бинарная операция записана без левого операнда")
                expect_operand = True
        elif token_type == TOKEN_LPAREN:
            if not expect_operand:
                raise ParseError("Пропущена операция перед открывающей скобкой")
            balance += 1
            expect_operand = True
        elif token_type == TOKEN_RPAREN:
            if expect_operand:
                raise ParseError("Пустые скобки или операция перед закрывающей скобкой")
            balance -= 1
            if balance < 0:
                raise ParseError("Несогласованные скобки")
            expect_operand = False

    if balance != 0:
        raise ParseError("Несогласованные скобки")
    if expect_operand:
        raise ParseError("Выражение не может заканчиваться операцией")


def shunting_yard(tokens: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Алгоритм сортировочной станции."""
    _validate_token_sequence(tokens)
    output = []
    stack = []

    for token_type, token_value in tokens:
        if token_type == TOKEN_VARIABLE:
            output.append((token_type, token_value))

        elif token_type == TOKEN_OPERATOR:
            while stack and stack[-1][0] == TOKEN_OPERATOR:
                top_op = stack[-1][1]
                top_priority = OPERATOR_PRIORITIES[top_op]
                curr_priority = OPERATOR_PRIORITIES[token_value]

                if (top_priority > curr_priority or
                    (top_priority == curr_priority and token_value not in UNARY_OPERATORS)):
                    output.append(stack.pop())
                else:
                    break
            stack.append((token_type, token_value))

        elif token_type == TOKEN_LPAREN:
            stack.append((token_type, token_value))

        elif token_type == TOKEN_RPAREN:
            while stack and stack[-1][0] != TOKEN_LPAREN:
                output.append(stack.pop())
            if stack and stack[-1][0] == TOKEN_LPAREN:
                stack.pop()
            else:
                raise ParseError("Несогласованные скобки")

    while stack:
        if stack[-1][0] == TOKEN_LPAREN:
            raise ParseError("Несогласованные скобки")
        output.append(stack.pop())

    return output


def evaluate_rpn(rpn: List[Tuple[str, str]], variables: Dict[str, int]) -> int:
    """Вычисляет выражение, записанное в обратной польской нотации."""
    stack = []

    for token_type, token_value in rpn:
        if token_type == TOKEN_VARIABLE:
            if token_value not in variables:
                raise ParseError(f"Не задано значение переменной: {token_value}")
            stack.append(variables[token_value])

        elif token_type == TOKEN_OPERATOR:
            if token_value in UNARY_OPERATORS:
                if not stack:
                    raise ParseError("Недостаточно операндов")
                operand = stack.pop()
                stack.append(1 - operand)

            elif token_value in BINARY_OPERATORS:
                if len(stack) < 2:
                    raise ParseError("Недостаточно операндов")
                right = stack.pop()
                left = stack.pop()

                if token_value == '&':
                    result = 1 if (left and right) else 0
                elif token_value == '|':
                    result = 1 if (left or right) else 0
                elif token_value == '->':
                    result = 1 if ((not left) or right) else 0
                elif token_value == '~':
                    result = left ^ right
                else:
                    raise ParseError(f"Неизвестная операция: {token_value}")

                stack.append(result)

    if len(stack) != 1:
        raise ParseError("Некорректное выражение")

    return stack[0]


class BooleanFunctionParser:
    def __init__(self, expression: str):
        self._expression = expression
        self._rpn = None
        self._variables = None
        self._parse()

    def _parse(self) -> None:
        tokens = tokenize(self._expression)
        self._rpn = shunting_yard(tokens)

        variables_set = {token_value for token_type, token_value in tokens if token_type == TOKEN_VARIABLE}
        self._variables = sorted(variables_set)

        if len(self._variables) > MAX_VARIABLES:
            raise ParseError(
                f"Поддерживается не более {MAX_VARIABLES} переменных. Найдено: {len(self._variables)}"
            )

    @property
    def variables(self) -> List[str]:
        return self._variables

    def evaluate(self, assignment: Dict[str, int]) -> int:
        return evaluate_rpn(self._rpn, assignment)

    def truth_table(self) -> List[Tuple[Tuple[int, ...], int]]:
        table = []
        n = len(self._variables)

        for i in range(1 << n):
            values = []
            for j in range(n):
                bit = (i >> (n - j - 1)) & 1
                values.append(bit)
            values_tuple = tuple(values)
            assignment = dict(zip(self._variables, values_tuple))
            table.append((values_tuple, self.evaluate(assignment)))

        return table

    def get_truth_table_vector(self) -> str:
        return ''.join(str(res) for _, res in self.truth_table())
