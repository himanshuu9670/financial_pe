"""Wrapper — run from project root: python backend/scripts/seed_demo_user.py"""

import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
script = root / "backend" / "scripts" / "seed_demo_user.py"
sys.exit(subprocess.call([sys.executable, str(script)]))
