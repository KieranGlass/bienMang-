import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database settings
DATABASE_URL = "sqlite:///nursery.db"
DEBUG = True

# Application settings
APP_NAME = "Bien Mangé"
VERSION = "1.0.0"

# File paths
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"