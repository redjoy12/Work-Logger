@echo off
REM Build script for Work Logger Windows executable
REM This script uses PyInstaller to create a standalone .exe file

echo ========================================
echo Work Logger - Build Executable
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller is not installed. Installing now...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo Building executable...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable using the spec file
pyinstaller work_logger.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Your executable is located at:
echo dist\WorkLogger.exe
echo.
echo You can now run the application by double-clicking the .exe file
echo or copy it to any location on your computer.
echo.
pause
