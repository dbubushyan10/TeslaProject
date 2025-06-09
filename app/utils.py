# app/utils.py

import sys
from pathlib import Path
from fastapi.templating import Jinja2Templates

# Определение базовой директории проекта
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "app" / "templates"  # папка "app/templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

print("BASE_DIR:", BASE_DIR)
print("TEMPLATES_DIR:", TEMPLATES_DIR)
