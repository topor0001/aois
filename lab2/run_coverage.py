"""Запуск тестов с отчётом покрытия."""

import os
import subprocess
import sys


def run_coverage():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 60)
    print("  ЗАПУСК ТЕСТОВ С ПОКРЫТИЕМ")
    print("=" * 60)

    subprocess.run(
        [sys.executable, "-m", "coverage", "run", "-m", "unittest", "discover", "-p", "test_*.py"],
        cwd=project_dir,
        text=True
    )

    print("\n" + "=" * 60)
    print("  ОТЧЁТ ПОКРЫТИЯ")
    print("=" * 60)

    subprocess.run(
        [sys.executable, "-m", "coverage", "report", "-m"],
        cwd=project_dir,
        text=True
    )


if __name__ == "__main__":
    run_coverage()
