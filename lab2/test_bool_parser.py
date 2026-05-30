import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bool_parser import (
    BooleanFunctionParser,
    ParseError,
    tokenize,
    shunting_yard,
    evaluate_rpn
)
from constants import TOKEN_VARIABLE, TOKEN_OPERATOR, TOKEN_LPAREN, TOKEN_RPAREN


class TestTokenize(unittest.TestCase):
    def test_variable(self):
        tokens = tokenize("a")
        self.assertEqual(tokens, [(TOKEN_VARIABLE, 'a')])

    def test_and(self):
        tokens = tokenize("a&b")
        self.assertEqual(
            tokens,
            [(TOKEN_VARIABLE, 'a'), (TOKEN_OPERATOR, '&'), (TOKEN_VARIABLE, 'b')]
        )

    def test_or(self):
        tokens = tokenize("a|b")
        self.assertEqual(
            tokens,
            [(TOKEN_VARIABLE, 'a'), (TOKEN_OPERATOR, '|'), (TOKEN_VARIABLE, 'b')]
        )

    def test_not(self):
        tokens = tokenize("!a")
        self.assertEqual(tokens, [(TOKEN_OPERATOR, '!'), (TOKEN_VARIABLE, 'a')])

    def test_implication(self):
        tokens = tokenize("a->b")
        self.assertEqual(
            tokens,
            [(TOKEN_VARIABLE, 'a'), (TOKEN_OPERATOR, '->'), (TOKEN_VARIABLE, 'b')]
        )

    def test_equivalence(self):
        tokens = tokenize("a~b")
        self.assertEqual(
            tokens,
            [(TOKEN_VARIABLE, 'a'), (TOKEN_OPERATOR, '~'), (TOKEN_VARIABLE, 'b')]
        )

    def test_equivalence_symbol(self):
        tokens = tokenize("a≡b")
        self.assertEqual(
            tokens,
            [(TOKEN_VARIABLE, 'a'), (TOKEN_OPERATOR, '~'), (TOKEN_VARIABLE, 'b')]
        )

    def test_parentheses(self):
        tokens = tokenize("(a&b)")
        self.assertEqual(
            tokens,
            [
                (TOKEN_LPAREN, '('),
                (TOKEN_VARIABLE, 'a'),
                (TOKEN_OPERATOR, '&'),
                (TOKEN_VARIABLE, 'b'),
                (TOKEN_RPAREN, ')')
            ]
        )

    def test_spaces(self):
        tokens = tokenize(" a & b ")
        self.assertEqual(
            tokens,
            [(TOKEN_VARIABLE, 'a'), (TOKEN_OPERATOR, '&'), (TOKEN_VARIABLE, 'b')]
        )

    def test_invalid_char(self):
        with self.assertRaises(ParseError):
            tokenize("a&z")


class TestShuntingYard(unittest.TestCase):
    def test_simple_and(self):
        tokens = tokenize("a&b")
        rpn = shunting_yard(tokens)
        self.assertEqual(len(rpn), 3)

    def test_simple_or(self):
        tokens = tokenize("a|b")
        rpn = shunting_yard(tokens)
        self.assertEqual(len(rpn), 3)

    def test_not(self):
        tokens = tokenize("!a")
        rpn = shunting_yard(tokens)
        self.assertEqual(len(rpn), 2)

    def test_parentheses(self):
        tokens = tokenize("(a&b)|c")
        rpn = shunting_yard(tokens)
        self.assertEqual(len(rpn), 5)


class TestEvaluateRPN(unittest.TestCase):
    def test_and_11(self):
        tokens = tokenize("a&b")
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn, {'a': 1, 'b': 1})
        self.assertEqual(result, 1)

    def test_and_10(self):
        tokens = tokenize("a&b")
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn, {'a': 1, 'b': 0})
        self.assertEqual(result, 0)

    def test_or_00(self):
        tokens = tokenize("a|b")
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn, {'a': 0, 'b': 0})
        self.assertEqual(result, 0)

    def test_or_01(self):
        tokens = tokenize("a|b")
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn, {'a': 0, 'b': 1})
        self.assertEqual(result, 1)

    def test_not(self):
        tokens = tokenize("!a")
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn, {'a': 0})
        self.assertEqual(result, 1)

    def test_implication(self):
        tokens = tokenize("a->b")
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn, {'a': 1, 'b': 0})
        self.assertEqual(result, 0)

    def test_equivalence_00(self):
        tokens = tokenize("a~b")
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn, {'a': 0, 'b': 0})
        self.assertEqual(result, 1)

    def test_equivalence_10(self):
        tokens = tokenize("a~b")
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn, {'a': 1, 'b': 0})
        self.assertEqual(result, 0)

    def test_equivalence_11(self):
        tokens = tokenize("a~b")
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn, {'a': 1, 'b': 1})
        self.assertEqual(result, 1)


class TestBooleanFunctionParser(unittest.TestCase):
    def test_simple_and(self):
        parser = BooleanFunctionParser("a&b")
        self.assertEqual(parser.variables, ['a', 'b'])
        self.assertEqual(parser.evaluate({'a': 1, 'b': 1}), 1)
        self.assertEqual(parser.evaluate({'a': 1, 'b': 0}), 0)

    def test_simple_or(self):
        parser = BooleanFunctionParser("a|b")
        self.assertEqual(parser.evaluate({'a': 0, 'b': 0}), 0)
        self.assertEqual(parser.evaluate({'a': 1, 'b': 0}), 1)

    def test_implication(self):
        parser = BooleanFunctionParser("a->b")
        self.assertEqual(parser.evaluate({'a': 1, 'b': 0}), 0)
        self.assertEqual(parser.evaluate({'a': 1, 'b': 1}), 1)
        self.assertEqual(parser.evaluate({'a': 0, 'b': 0}), 1)

    def test_equivalence(self):
        parser = BooleanFunctionParser("a~b")
        self.assertEqual(parser.evaluate({'a': 0, 'b': 0}), 1)
        self.assertEqual(parser.evaluate({'a': 1, 'b': 0}), 0)
        self.assertEqual(parser.evaluate({'a': 1, 'b': 1}), 1)

    def test_equivalence_vector(self):
        parser = BooleanFunctionParser("a~b")
        self.assertEqual(parser.get_truth_table_vector(), "1001")

    def test_not(self):
        parser = BooleanFunctionParser("!a")
        self.assertEqual(parser.evaluate({'a': 0}), 1)
        self.assertEqual(parser.evaluate({'a': 1}), 0)

    def test_parentheses(self):
        parser = BooleanFunctionParser("(a&b)|c")
        self.assertEqual(parser.evaluate({'a': 1, 'b': 0, 'c': 1}), 1)
        self.assertEqual(parser.evaluate({'a': 1, 'b': 0, 'c': 0}), 0)

    def test_complex_expression(self):
        parser = BooleanFunctionParser("!(!a->!b)|c")
        self.assertIsNotNone(parser.truth_table())

    def test_equivalence_implication_expression_vector(self):
        parser = BooleanFunctionParser("(a~b)->!c")
        self.assertEqual(parser.get_truth_table_vector(), "10111110")

    def test_too_many_variables(self):
        with self.assertRaises(ParseError):
            BooleanFunctionParser("a&b&c&d&e&f")

    def test_invalid_character(self):
        with self.assertRaises(ParseError):
            BooleanFunctionParser("a&b&z")

    def test_truth_table_size(self):
        parser = BooleanFunctionParser("a&b")
        tt = parser.truth_table()
        self.assertEqual(len(tt), 4)


if __name__ == "__main__":
    unittest.main()