import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bool_parser import BooleanFunctionParser
from truth_table import TruthTable
from differentiation import BooleanDerivative


class TestBooleanDerivative(unittest.TestCase):
    def setUp(self):
        parser = BooleanFunctionParser("a~b")
        tt = TruthTable(parser.variables, parser.truth_table())
        self.deriv = BooleanDerivative(tt)
    
    def test_partial(self):
        result = self.deriv.partial('a')
        self.assertEqual(len(result), 4)
    
    def test_mixed(self):
        result = self.deriv.mixed(['a', 'b'])
        self.assertEqual(len(result), 4)
    
    def test_format_result(self):
        result = self.deriv.partial('a')
        lines = self.deriv.format_result(result)
        self.assertEqual(len(lines), 4)
    
    def test_partial_vector(self):
        vector = self.deriv.partial_vector('a')
        self.assertEqual(len(vector), 4)
    
    def test_and_function(self):
        parser = BooleanFunctionParser("a&b")
        tt = TruthTable(parser.variables, parser.truth_table())
        deriv = BooleanDerivative(tt)
        result = deriv.partial('a')
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()