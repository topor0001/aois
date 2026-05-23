import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from truth_table import TruthTable
from zhegalkin import ZhegalkinPolynomial


class TestZhegalkin(unittest.TestCase):
    def test_and_polynomial(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 0),
            ((1, 0), 0),
            ((1, 1), 1),
        ]
        tt = TruthTable(variables, table)
        z = ZhegalkinPolynomial(tt)
        self.assertEqual(z.compute(), 'a&b')
    
    def test_xor_polynomial(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 1),
            ((1, 0), 1),
            ((1, 1), 0),
        ]
        tt = TruthTable(variables, table)
        z = ZhegalkinPolynomial(tt)
        result = z.compute()
        # XOR can be represented as a XOR b
        self.assertIn(result, ['a XOR b', 'b XOR a'])
    
    def test_const_zero(self):
        variables = ['a']
        table = [((0,), 0), ((1,), 0)]
        tt = TruthTable(variables, table)
        z = ZhegalkinPolynomial(tt)
        self.assertEqual(z.compute(), '0')
    
    def test_const_one(self):
        variables = ['a']
        table = [((0,), 1), ((1,), 1)]
        tt = TruthTable(variables, table)
        z = ZhegalkinPolynomial(tt)
        self.assertEqual(z.compute(), '1')
    
    def test_get_coefficients(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 1),
            ((1, 0), 1),
            ((1, 1), 0),
        ]
        tt = TruthTable(variables, table)
        z = ZhegalkinPolynomial(tt)
        coeffs = z.get_coefficients()
        self.assertEqual(len(coeffs), 4)


if __name__ == "__main__":
    unittest.main()