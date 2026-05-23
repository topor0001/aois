import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from truth_table import TruthTable
from normal_forms import NormalForms


class TestNormalForms(unittest.TestCase):
    def setUp(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 1),
            ((1, 0), 1),
            ((1, 1), 1),
        ]
        tt = TruthTable(variables, table)
        self.forms = NormalForms(tt)
    
    def test_get_sdnf(self):
        sdnf, nums = self.forms.get_sdnf()
        self.assertEqual(nums, [1, 2, 3])
        self.assertIn('a', sdnf)
        self.assertIn('b', sdnf)
    
    def test_get_sknf(self):
        sknf, nums = self.forms.get_sknf()
        self.assertEqual(nums, [0])
        self.assertIn('a', sknf)
        self.assertIn('b', sknf)
    
    def test_get_index_form(self):
        self.assertEqual(self.forms.get_index_form(), "0111")
    
    def test_sdnf_numeric(self):
        self.assertEqual(self.forms.get_sdnf_numeric(), [1, 2, 3])
    
    def test_sknf_numeric(self):
        self.assertEqual(self.forms.get_sknf_numeric(), [0])
    
    def test_const_zero(self):
        variables = ['a']
        table = [((0,), 0), ((1,), 0)]
        tt = TruthTable(variables, table)
        forms = NormalForms(tt)
        sdnf, nums = forms.get_sdnf()
        self.assertEqual(sdnf, '0')
        self.assertEqual(nums, [])
    
    def test_const_one(self):
        variables = ['a']
        table = [((0,), 1), ((1,), 1)]
        tt = TruthTable(variables, table)
        forms = NormalForms(tt)
        sknf, nums = forms.get_sknf()
        self.assertEqual(sknf, '1')
        self.assertEqual(nums, [])


if __name__ == "__main__":
    unittest.main()