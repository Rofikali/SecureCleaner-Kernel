@echo off
echo [L6 KERNEL] STARTING ICON-EMBEDDED BUILD...

:: 1. Force kill existing app
taskkill /F /IM SmartCleaner.exe /T >nul 2>&1

:: 2. Clean artifacts
if exist build rd /s /q build
if exist dist rd /s /q dist

call .venv\Scripts\activate

:: 3. Build with Icon Support
:: --icon: Sets the .exe icon
:: --add-data: Packs the icon inside the EXE so get_resource_path can find it
pyinstaller --noconsole --onefile ^
--name "SmartCleaner" ^
--icon "app_icon.ico" ^
--add-data "app_icon.ico;." ^
--paths . ^
--collect-submodules core ^
--collect-submodules ui ^
--collect-submodules utils ^
--hidden-import=pystray._win32 ^
main.py

echo [OK] DEPLOYMENT READY WITH CUSTOM ICON!
pause
