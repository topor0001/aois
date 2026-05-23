import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from truth_table import TruthTable


class TestTruthTable(unittest.TestCase):
    def setUp(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 0),
            ((1, 0), 0),
            ((1, 1), 1),
        ]
        self.tt = TruthTable(variables, table)
    
    def test_variables(self):
        self.assertEqual(self.tt.variables, ['a', 'b'])
    
    def test_n(self):
        self.assertEqual(self.tt.n, 2)
    
    def test_get_vector(self):
        self.assertEqual(self.tt.get_vector(), "0001")
    
    def test_get_ones_indices(self):
        self.assertEqual(self.tt.get_ones_indices(), [3])
    
    def test_get_zeros_indices(self):
        self.assertEqual(self.tt.get_zeros_indices(), [0, 1, 2])
    
    def test_index_to_values(self):
        self.assertEqual(TruthTable.index_to_values(3, 2), (1, 1))
    
    def test_get_value(self):
        self.assertEqual(self.tt.get_value((1, 1)), 1)
        self.assertEqual(self.tt.get_value((0, 0)), 0)
    
    def test_is_const_zero(self):
        self.assertFalse(self.tt.is_const_zero())
    
    def test_is_const_one(self):
        self.assertFalse(self.tt.is_const_one())
    
    def test_const_zero_function(self):
        variables = ['a']
        table = [((0,), 0), ((1,), 0)]
        tt = TruthTable(variables, table)
        self.assertTrue(tt.is_const_zero())
    
    def test_const_one_function(self):
        variables = ['a']
        table = [((0,), 1), ((1,), 1)]
        tt = TruthTable(variables, table)
        self.assertTrue(tt.is_const_one())


if __name__ == "__main__":
    unittest.main()