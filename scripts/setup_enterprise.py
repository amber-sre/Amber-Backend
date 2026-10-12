#!/usr/bin/env python3
"""
Amber SRE Engine — Commercial / Enterprise Edition Setup Wizard
Delegates to the interactive Commercial Setup Wizard in setup_wizards.py
"""

import os
import sys
from pathlib import Path

# Ensure repo root is in sys.path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from scripts.setup_wizards import run_commercial_setup

if __name__ == "__main__":
    run_commercial_setup()
