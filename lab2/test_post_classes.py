import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from truth_table import TruthTable
from post_classes import PostClasses


class TestPostClasses(unittest.TestCase):
    def test_t0_and_function(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 0),
            ((1, 0), 0),
            ((1, 1), 1),
        ]
        tt = TruthTable(variables, table)
        post = PostClasses(tt)
        self.assertTrue(post.is_t0())
    
    def test_t1_and_function(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 0),
            ((1, 0), 0),
            ((1, 1), 1),
        ]
        tt = TruthTable(variables, table)
        post = PostClasses(tt)
        # AND function preserves 1 because f(1,1)=1
        self.assertTrue(post.is_t1())
    
    def test_t1_const_one(self):
        variables = ['a']
        table = [((0,), 1), ((1,), 1)]
        tt = TruthTable(variables, table)
        post = PostClasses(tt)
        self.assertTrue(post.is_t1())
    
    def test_self_dual_not(self):
        variables = ['a']
        table = [((0,), 1), ((1,), 0)]
        tt = TruthTable(variables, table)
        post = PostClasses(tt)
        self.assertTrue(post.is_self_dual())
    
    def test_monotonic_and(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 0),
            ((1, 0), 0),
            ((1, 1), 1),
        ]
        tt = TruthTable(variables, table)
        post = PostClasses(tt)
        self.assertTrue(post.is_monotonic())
    
    def test_not_monotonic(self):
        variables = ['a']
        table = [((0,), 1), ((1,), 0)]
        tt = TruthTable(variables, table)
        post = PostClasses(tt)
        self.assertFalse(post.is_monotonic())
    
    def test_linear_xor(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 1),
            ((1, 0), 1),
            ((1, 1), 0),
        ]
        tt = TruthTable(variables, table)
        post = PostClasses(tt)
        self.assertTrue(post.is_linear())
    
    def test_get_all(self):
        variables = ['a', 'b']
        table = [
            ((0, 0), 0),
            ((0, 1), 0),
            ((1, 0), 0),
            ((1, 1), 1),
        ]
        tt = TruthTable(variables, table)
        post = PostClasses(tt)
        all_classes = post.get_all()
        self.assertEqual(len(all_classes), 5)
        self.assertIsNotNone(all_classes)


if __name__ == "__main__":
    unittest.main()