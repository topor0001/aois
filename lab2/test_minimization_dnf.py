import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bool_parser import BooleanFunctionParser
from truth_table import TruthTable
from minimization_dnf import MinimizationDNF


class TestMinimizationDNF(unittest.TestCase):
    def test_and_function(self):
        parser = BooleanFunctionParser("a&b")
        tt = TruthTable(parser.variables, parser.truth_table())
        minimizer = MinimizationDNF(tt)
        result, stages = minimizer.minimize_with_stages()
        self.assertIsNotNone(result)
    
    def test_or_function(self):
        parser = BooleanFunctionParser("a|b")
        tt = TruthTable(parser.variables, parser.truth_table())
        minimizer = MinimizationDNF(tt)
        result, stages = minimizer.minimize_with_stages()
        self.assertIsNotNone(result)
    
    def test_const_zero(self):
        parser = BooleanFunctionParser("a&!a")
        tt = TruthTable(parser.variables, parser.truth_table())
        minimizer = MinimizationDNF(tt)
        result, stages = minimizer.minimize_with_stages()
        self.assertEqual(result, '0')
    
    def test_const_one(self):
        parser = BooleanFunctionParser("a|!a")
        tt = TruthTable(parser.variables, parser.truth_table())
        minimizer = MinimizationDNF(tt)
        result, stages = minimizer.minimize_with_stages()
        self.assertEqual(result, '1')
    
    def test_majority_function(self):
        parser = BooleanFunctionParser("(a&b)|(a&c)|(b&c)")
        tt = TruthTable(parser.variables, parser.truth_table())
        minimizer = MinimizationDNF(tt)
        result, stages = minimizer.minimize_with_stages()
        self.assertIsNotNone(result)
    
    def test_get_prime_implicants(self):
        parser = BooleanFunctionParser("(a&b)|(a&c)")
        tt = TruthTable(parser.variables, parser.truth_table())
        minimizer = MinimizationDNF(tt)
        primes = minimizer.get_prime_implicants()
        self.assertGreater(len(primes), 0)


if __name__ == "__main__":
    unittest.main()