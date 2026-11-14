#!/usr/bin/env python3
"""Run the existing offline suite and fixture validation from any directory."""
import os
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO))
os.chdir(REPO)


def main():
    # Do not read a real credential. Tests needing one supply their own fake value.
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    with patch.object(socket, "socket", side_effect=AssertionError("Network forbidden in offline checks")):
        suite = unittest.defaultTestLoader.discover(str(REPO / "evals/tests"))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            return 1
        from evals.runner import main as runner_main
        return runner_main(["validate"])


if __name__ == "__main__":
    raise SystemExit(main())
