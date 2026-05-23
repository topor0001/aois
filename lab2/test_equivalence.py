import unittest

from bool_parser import BooleanFunctionParser, ParseError
from karnaugh import KarnaughMap
from minimization_cnf import MinimizationCNF
from minimization_dnf import MinimizationDNF
from truth_table import TruthTable


def evaluate_expression(expression, variables, values):
    if expression == '0':
        return 0
    if expression == '1':
        return 1
    parser = BooleanFunctionParser(expression)
    return parser.evaluate(dict(zip(variables, values)))


class TestEquivalentResults(unittest.TestCase):
    def assert_equivalent(self, source_expression):
        parser = BooleanFunctionParser(source_expression)
        truth_table = TruthTable(parser.variables, parser.truth_table())
        expressions = [
            MinimizationDNF(truth_table).minimize_with_stages()[0],
            MinimizationCNF(truth_table).minimize_with_stages()[0],
        ]
        if truth_table.n <= 4:
            expressions.append(KarnaughMap(truth_table).minimize_dnf()[0])
            expressions.append(KarnaughMap(truth_table).minimize_cnf()[0])

        for result_expression in expressions:
            for values, expected in truth_table.table:
                actual = evaluate_expression(result_expression, truth_table.variables, values)
                self.assertEqual(actual, expected, msg=result_expression)

    def test_single_variable(self):
        self.assert_equivalent('a')

    def test_implication_expression(self):
        self.assert_equivalent('!(!a->!b)|c')

    def test_majority_expression(self):
        self.assert_equivalent('(a&b)|(a&c)|(b&c)')

    def test_four_variables_expression(self):
        self.assert_equivalent('(a&b)|(c&d)')


class TestInvalidExpressions(unittest.TestCase):
    def assert_parse_error(self, expression):
        with self.assertRaises(ParseError):
            BooleanFunctionParser(expression)

    def test_empty_expression(self):
        self.assert_parse_error('')

    def test_double_binary_operator(self):
        self.assert_parse_error('a&&b')

    def test_expression_ends_with_operator(self):
        self.assert_parse_error('a->')

    def test_missing_operator_between_variables(self):
        self.assert_parse_error('ab')

    def test_empty_parentheses(self):
        self.assert_parse_error('()')


if __name__ == '__main__':
    unittest.main()
