"""
conftest.py – ensures the backend/app package is importable
when pytest is run from the d:\\Mig_Guard\\backend directory.
"""
import sys
from pathlib import Path

# Insert the backend/ directory onto sys.path so that
# `from app.rules import checks` etc. resolve correctly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
