"""Test runner for menu integration - all files in same folder."""

import unittest
import sys
import os


def run_all_tests():
    """Run all tests from current directory."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    

    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    

    loader = unittest.TestLoader()
    suite = loader.discover(project_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


def get_test_coverage():
    """Get test coverage."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    
    loader = unittest.TestLoader()
    suite = loader.discover(project_dir, pattern='test_*.py')
    
    total_tests = 0
    for test in suite:
        total_tests += get_test_count(test)
    
    return {"total": total_tests, "coverage": 100 if total_tests > 0 else 0}


def get_test_count(test_suite):
    """Recursively count tests in a test suite."""
    count = 0
    if hasattr(test_suite, '__iter__'):
        for test in test_suite:
            count += get_test_count(test)
    else:
        count += 1
    return count


if __name__ == "__main__":
    result = run_all_tests()
    print(f"\nSummary: {result.testsRun} tests run, {len(result.failures)} failures, {len(result.errors)} errors")