@echo off
echo [L6 QUALITY] Formatting and Linting...
call .venv\Scripts\activate
:: Sort imports and fix lint errors
python -m ruff check . --fix
:: Format code to Google/Black standards
python -m black .
echo [OK] Code is now Kernel-Grade.
pause
