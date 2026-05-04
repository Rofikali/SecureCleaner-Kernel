@echo off
echo [L6 QUALITY] Running Unit Tests...
call .venv\Scripts\activate
python -m pytest tests/ -v
pause
