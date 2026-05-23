import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from implicant import Implicant


class TestImplicant(unittest.TestCase):
    def setUp(self):
        self.variables = ['a', 'b', 'c']
    
    def test_from_binary(self):
        imp = Implicant.from_binary((1, 0, 1), self.variables)
        self.assertEqual(imp.mask, (1, 0, 1))
    
    def test_to_string(self):
        imp = Implicant((1, 0, -1), self.variables)
        result = imp.to_string()
        self.assertIn(result, ['a&!b', '(a&!b)'])
    
    def test_to_string_single(self):
        imp = Implicant((1, -1, -1), self.variables)
        self.assertEqual(imp.to_string(), 'a')
    
    def test_to_string_empty(self):
        imp = Implicant((-1, -1, -1), self.variables)
        self.assertEqual(imp.to_string(), '1')
    
    def test_covers(self):
        imp = Implicant((1, -1, 0), self.variables)
        self.assertTrue(imp.covers((1, 0, 0)))
        self.assertTrue(imp.covers((1, 1, 0)))
        self.assertFalse(imp.covers((0, 0, 0)))
    
    def test_can_combine(self):
        a = Implicant((1, 0, 1), self.variables)
        b = Implicant((1, 0, 0), self.variables)
        self.assertTrue(Implicant.can_combine(a, b))
    
    def test_cannot_combine(self):
        a = Implicant((1, 0, 1), self.variables)
        b = Implicant((0, 1, 0), self.variables)
        self.assertFalse(Implicant.can_combine(a, b))
    
    def test_combine(self):
        a = Implicant((1, 0, 1), self.variables)
        b = Implicant((1, 0, 0), self.variables)
        combined = Implicant.combine(a, b)
        self.assertEqual(combined.mask, (1, 0, -1))
    
    def test_size(self):
        imp = Implicant((1, -1, 0), self.variables)
        self.assertEqual(imp.size(), 2)
    
    def test_eq(self):
        a = Implicant((1, 0, -1), self.variables)
        b = Implicant((1, 0, -1), self.variables)
        self.assertEqual(a, b)
    
    def test_hash(self):
        a = Implicant((1, 0, -1), self.variables)
        b = Implicant((1, 0, -1), self.variables)
        self.assertEqual(hash(a), hash(b))
    
    def test_from_string(self):
        imp = Implicant.from_string('a&!b', self.variables)
        self.assertEqual(imp.mask, (1, 0, -1))


if __name__ == "__main__":
    unittest.main()