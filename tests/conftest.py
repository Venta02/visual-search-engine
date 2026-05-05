"""Shared pytest fixtures."""

import os
import sys
from pathlib import Path

# Make src importable when running pytest from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use development settings for tests
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("LOG_LEVEL", "WARNING")
