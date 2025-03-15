# src/tests/conftest.py
import pytest
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Setup logging directory
log_dir = Path(__file__).parent / 'log'
log_dir.mkdir(exist_ok=True)