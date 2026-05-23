import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bool_parser import BooleanFunctionParser
from truth_table import TruthTable


class TestCNFSimple(unittest.TestCase):
    
    def test_and_function_exists(self):
        parser = BooleanFunctionParser("a&b")
        self.assertIsNotNone(parser)
    
    def test_truth_table_exists(self):
        parser = BooleanFunctionParser("a&b")
        tt = parser.truth_table()
        self.assertEqual(len(tt), 4)


if __name__ == "__main__":
    unittest.main()