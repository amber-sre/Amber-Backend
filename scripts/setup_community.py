#!/usr/bin/env python3
"""
Amber SRE Engine — Free Community Edition Setup Wizard
Delegates to the interactive Community Setup Wizard in setup_wizards.py
"""

import os
import sys
from pathlib import Path

# Ensure repo root is in sys.path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from scripts.setup_wizards import run_community_setup

if __name__ == "__main__":
    run_community_setup()
