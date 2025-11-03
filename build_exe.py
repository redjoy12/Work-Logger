#!/usr/bin/env python3
"""
Build script for Work Logger executable
This script uses PyInstaller to create a standalone executable
Works on Windows, macOS, and Linux
"""

import subprocess
import sys
import os
import shutil

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller  # pylint: disable=import-outside-toplevel,unused-import
        print("✓ PyInstaller is installed")
        return True
    except ImportError:
        print("PyInstaller is not installed. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name} directory...")
            shutil.rmtree(dir_name)

def build_executable():
    """Build the executable using PyInstaller."""
    print("\n" + "="*50)
    print("Work Logger - Build Executable")
    print("="*50 + "\n")

    # Check PyInstaller
    if not check_pyinstaller():
        return False

    # Clean previous builds
    clean_build_dirs()

    # Build using spec file
    print("\nBuilding executable...")
    try:
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "work_logger.spec"])

        print("\n" + "="*50)
        print("Build Complete!")
        print("="*50)

        # Find the executable
        if sys.platform == "win32":
            exe_path = os.path.join("dist", "WorkLogger.exe")
        else:
            exe_path = os.path.join("dist", "WorkLogger")

        if os.path.exists(exe_path):
            print("\nYour executable is located at:")
            print(f"  {os.path.abspath(exe_path)}")
            print("\nYou can now run the application by:")
            if sys.platform == "win32":
                print("  - Double-clicking the .exe file")
            else:
                print(f"  - Running: ./{exe_path}")
            print("  - Copying it to any location on your computer")
        else:
            print(f"\nWarning: Could not find executable at expected location: {exe_path}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error: {e}")
        return False

if __name__ == "__main__":
    success = build_executable()  # pylint: disable=invalid-name

    if not success:
        print("\nBuild failed. Please check the error messages above.")
        sys.exit(1)

    print("\n")
    sys.exit(0)
