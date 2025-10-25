# Building Work Logger Executable

This document provides detailed information about building standalone executables for Work Logger.

## Quick Start

### Windows
```batch
build_exe.bat
```

### All Platforms (Windows, macOS, Linux)
```bash
python build_exe.py
```

## Prerequisites

1. **Python 3.6 or higher** installed on your system
2. **PyInstaller** (will be installed automatically by the build scripts)
3. **tkinter** must be included with your Python installation
   - Windows: tkinter comes pre-installed with Python
   - macOS: tkinter comes pre-installed with Python
   - Linux: Install with `sudo apt-get install python3-tk` (Debian/Ubuntu) or equivalent

## Build Output

After running the build script, you'll find:

- **Executable**: `dist/WorkLogger.exe` (Windows) or `dist/WorkLogger` (Linux/macOS)
- **Build artifacts**: `build/` directory (can be deleted)
- **Distribution folder**: `dist/` directory containing the executable

## Customization

### Changing the Executable Icon

1. Create or obtain an `.ico` file (Windows) or `.icns` file (macOS)
2. Edit `work_logger.spec` file
3. Update the `icon` parameter in the `EXE` section:
   ```python
   icon='path/to/your/icon.ico'  # For Windows
   ```

### Reducing Executable Size

The executable can be optimized for size by:

1. **Using UPX compression** (already enabled in the spec file)
2. **Excluding unused modules**: Edit `work_logger.spec` and add modules to `excludes`
3. **Using onefile mode** (already configured)

### Building for Distribution

When building for distribution to other users:

1. **Build on the target platform**:
   - Build Windows .exe on Windows
   - Build macOS app on macOS
   - Build Linux binary on Linux

2. **Test the executable** on a clean system without Python installed

3. **Include a README** with basic usage instructions

## Troubleshooting

### "tkinter installation is broken" warning

This warning may appear on Linux systems that don't have tkinter properly installed. To fix:

```bash
# Debian/Ubuntu
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

### Executable won't run on other computers

- Make sure the target computer has the same architecture (32-bit vs 64-bit)
- On Windows, the Visual C++ Redistributable may be required
- Build on the oldest supported OS version for maximum compatibility

### Antivirus false positives

Some antivirus software may flag PyInstaller executables as suspicious. This is a known issue with PyInstaller. To mitigate:

1. Sign your executable with a code signing certificate
2. Submit the executable to antivirus vendors as a false positive
3. Provide the source code alongside the executable

### Large executable size

The one-file executable includes Python and all dependencies. Typical size:

- Windows: ~15-25 MB
- Linux: ~15-20 MB
- macOS: ~15-25 MB

This is normal for PyInstaller executables.

## Advanced Options

### Building with Debug Mode

Edit `work_logger.spec` and change:
```python
debug=True,
console=True,  # Shows console window with debug output
```

### Building with Custom Python Path

```bash
/path/to/python -m PyInstaller work_logger.spec
```

## Platform-Specific Notes

### Windows
- The `.exe` file is completely standalone
- No Python installation required on target machine
- Console window is hidden by default (see spec file)

### macOS
- May need to create a `.app` bundle for better integration
- Users may need to allow the app in Security & Privacy settings
- Consider code signing for distribution

### Linux
- The executable may not work across all distributions
- Build on the oldest distribution you want to support
- Consider using AppImage or Flatpak for better compatibility

## References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [PyInstaller Spec Files](https://pyinstaller.org/en/stable/spec-files.html)
- [Common Issues](https://pyinstaller.org/en/stable/when-things-go-wrong.html)
