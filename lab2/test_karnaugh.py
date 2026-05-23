import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bool_parser import BooleanFunctionParser
from truth_table import TruthTable
from karnaugh import KarnaughMap


class TestKarnaughMap(unittest.TestCase):
    def test_2var_and(self):
        parser = BooleanFunctionParser("a&b")
        tt = TruthTable(parser.variables, parser.truth_table())
        kmap = KarnaughMap(tt)
        result, map_str = kmap.minimize_dnf()
        self.assertIsNotNone(result)
    
    def test_2var_or(self):
        parser = BooleanFunctionParser("a|b")
        tt = TruthTable(parser.variables, parser.truth_table())
        kmap = KarnaughMap(tt)
        result, map_str = kmap.minimize_dnf()
        self.assertIsNotNone(result)
    
    def test_3var(self):
        parser = BooleanFunctionParser("(a&b)|c")
        tt = TruthTable(parser.variables, parser.truth_table())
        kmap = KarnaughMap(tt)
        result, map_str = kmap.minimize_dnf()
        self.assertIsNotNone(result)
    
    def test_4var(self):
        parser = BooleanFunctionParser("(a&b)|(c&d)")
        tt = TruthTable(parser.variables, parser.truth_table())
        kmap = KarnaughMap(tt)
        result, map_str = kmap.minimize_dnf()
        self.assertIsNotNone(result)
    
    def test_cnf_2var(self):
        parser = BooleanFunctionParser("a&b")
        tt = TruthTable(parser.variables, parser.truth_table())
        kmap = KarnaughMap(tt)
        result, map_str = kmap.minimize_cnf()
        self.assertIsNotNone(result)
    
    def test_get_karnaugh_map(self):
        parser = BooleanFunctionParser("a&b")
        tt = TruthTable(parser.variables, parser.truth_table())
        kmap = KarnaughMap(tt)
        k_map = kmap.get_karnaugh_map(target=1)
        self.assertEqual(len(k_map), 2)


if __name__ == "__main__":
    unittest.main()